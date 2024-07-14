from main import app
from flask import Flask, render_template, request, redirect, session, url_for, flash
from models import RoleEnum ,db, User, Sponsor, Influencer ,Campaign, AdRequest, Flag
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime
from forms import CampaignForm,ProfileForm
# routes

# decorator
def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'username' not in session:
            flash("You need to login first")
            return redirect(url_for('login'))
        user = User.query.filter_by(username=session['username']).first()
        if not user:
            session.pop('username')
            return redirect(url_for('login'))
        return func(*args, **kwargs)
    return wrapper

def admin_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'username' not in session:
            flash("You need to login first")
            return redirect(url_for('login'))
        user = User.query.filter_by(username=session['username']).first()
        if not user:
            session.pop('username')
            return redirect(url_for('login'))
        if user.role!=RoleEnum.ADMIN:
            flash("You are not authorized to visit this page")
            return redirect(url_for('home'))
        return func(*args, **kwargs)
    return wrapper

@app.route('/')
@login_required
def home():
    username=session['username']
    user = User.query.filter_by(username=username).first()
    if user.role ==RoleEnum.SPONSOR:
        return redirect(url_for('sponsor_home'))
    elif user.role ==RoleEnum.INFLUENCER:
        return redirect(url_for('influencer_home'))
    else:
        return redirect(url_for('admin'))
    

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login_post():
    username = request.form.get('username')
    password = request.form.get('password')
    user = User.query.filter_by(username=username).first()
    if not user or not check_password_hash(user.passhash, password):
        flash("Username or password is incorrect")
        return redirect(url_for('login'))
    session['username'] = username
    return redirect(url_for('home'))

@app.route('/sponsor_register')
def sponsor_register():
    return render_template('sponsor_register.html')

@app.route('/influencer_register')
def influencer_register():
    return render_template('influencer_register.html')

@app.route('/logout')
@login_required
def logout():
    session.pop('username')
    return redirect(url_for('login'))

@app.route('/admin')
@admin_required
def admin():
    users = User.query.all()
    return render_template('admin_home.html', users=users)


@app.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    query = request.form.get('search') if request.method == 'POST' else request.args.get('search')
    campaigns = []
    if query:
        campaigns = Campaign.query.filter(Campaign.title.ilike(f'%{query}%')).all()

    return render_template('search.html', query=query, campaigns=campaigns)


@app.route('/sponsor_register', methods=['POST'])
def sponsor_register_post():
    email = request.form.get('email')
    username = request.form.get('username')
    password = request.form.get('password')
    confirm = request.form.get('confirm')
    companyname=request.form.get('company_name')
    name=request.form.get('name')
    industry=request.form.get('industry')
    budget=request.form.get('budget')

    # all not nullable inputs are not empty
    if not username or not password or not confirm or not email or not companyname or not name or not industry or not budget:
        flash("Please fill all the mandatory fields")
        return redirect(url_for('sponsor_register'))

    # confirm and password should be same
    if not password == confirm:
        flash("Confirm and Password are not same")
        return redirect(url_for('sponsor_register'))

    # username should be unique
    user = User.query.filter_by(username=username).first()
    if user:
        flash("Please choose another username, selected username is taken")
        return redirect(url_for('sponsor_register'))


    passhash = generate_password_hash(password)

    user = User(email=email, username=username, passhash=passhash,role=RoleEnum.SPONSOR)
    db.session.add(user)
    db.session.commit()
    user = User.query.filter_by(username=username).first()
    sponsor=Sponsor(user_id=user.id,company_name=companyname,individual_name=name,industry=industry,budget=budget)
    db.session.add(sponsor)
    db.session.commit()
    flash("Registration Successful, Please login to continue")
    return redirect(url_for('login'))

@app.route('/influencer_register', methods=['POST'])
def influencer_register_post():
    email = request.form.get('email')
    username = request.form.get('username')
    password = request.form.get('password')
    confirm = request.form.get('confirm')
    name=request.form.get('name')
    category=request.form.get('category')
    platform=request.form.get('platform')
    reach=request.form.get('reach')

    # all not nullable inputs are not empty
    if not username or not password or not confirm or not email or not name or not category or not platform or not reach:
        flash("Please fill all the mandatory fields")
        return redirect(url_for('influencer_register'))

    # confirm and password should be same
    if not password == confirm:
        flash("Confirm and Password are not same")
        return redirect(url_for('influencer_register'))

    # username should be unique
    user = User.query.filter_by(username=username).first()
    if user:
        flash("Please choose another username, selected username is taken")
        return redirect(url_for('influencer_register'))


    passhash = generate_password_hash(password)

    user = User(email=email, username=username, passhash=passhash,role=RoleEnum.INFLUENCER)
    db.session.add(user)
    db.session.commit()
    user = User.query.filter_by(username=username).first()
    influencer=Influencer(user_id=user.id,name=name,category=category,platform=platform,reach=reach)
    db.session.add(influencer)
    db.session.commit()
    flash("Registration Successful, Please login to continue")
    return redirect(url_for('login'))


@app.route('/profile')
@login_required
def profile():
    username=session['username']
    user = User.query.filter_by(username=username).first()
    if user.role==RoleEnum.SPONSOR:
        sponsor = Sponsor.query.filter_by(user_id=user.id).first()
        return render_template('profile_sponsor.html',user=user,sponsor=sponsor)    
    elif user.role==RoleEnum.INFLUENCER:
        influencer = Influencer.query.filter_by(user_id=user.id).first()    
        return render_template('profile_influencer.html',user=user,influencer=influencer)    
    if user.role==RoleEnum.SPONSOR:
        return render_template('profile_admin.html',user=user)    

@app.route('/profile/update', methods=['GET', 'POST'])
@login_required
def update_profile():
    form = ProfileForm()
    username = session['username']
    user = User.query.filter_by(username=username).first()

    if form.validate_on_submit():
        confirm = form.confirm.data
        password = form.password.data

        if check_password_hash(user.passhash, confirm):
            if password:
                user.passhash = generate_password_hash(password)
        else:
            flash("Entered current password is incorrect", 'danger')
            return redirect(url_for('update_profile'))

        user.username = form.username.data
        user.email = form.email.data

        if user.role == RoleEnum.SPONSOR:
            sponsor = Sponsor.query.filter_by(user_id=user.id).first()
            sponsor.company_name = form.company_name.data
            sponsor.individual_name = form.individual_name.data
            sponsor.industry = form.industry.data
            sponsor.budget = form.budget.data
        elif user.role == RoleEnum.INFLUENCER:
            influencer = Influencer.query.filter_by(user_id=user.id).first()
            influencer.name = form.name.data
            influencer.category = form.category.data
            influencer.platform = form.platform.data
            influencer.reach = form.reach.data

        db.session.commit()
        flash('Profile updated successfully.', 'success')
        return redirect(url_for('profile'))
    if user.role==RoleEnum.SPONSOR:
        return render_template('update_sponsor.html', form=form, user=user)
    elif user.role==RoleEnum.INFLUENCER:
        return render_template('update_influencer.html', form=form, user=user)
    else:
        return render_template('update_admin.html', form=form, user=user)


@app.route('/influencer/home')
@login_required
def influencer_home():
    username=session['username']
    user = User.query.filter_by(username=username).first()
    if user.role !=RoleEnum.INFLUENCER:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('index'))

    campaigns = Campaign.query.filter_by(visibility='public').all()

    return render_template('influencer_home.html', campaigns=campaigns,user=user)

@app.route('/sponsor/home')
@login_required
def sponsor_home():
    username=session['username']
    user = User.query.filter_by(username=username).first()
    if user.role !=RoleEnum.SPONSOR:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('home'))

    sponsor = Sponsor.query.filter_by(user_id=user.id).first()
    #campaigns = Campaign.query.filter_by(sponsor_id=sponsor.id).all()

    #return render_template('sponsor_home.html',campaigns=campaigns,user=user)
    return render_template('sponsor_home.html',user=user)

@app.route('/campaigns')
@login_required
def campaigns():
    username=session['username']
    user = User.query.filter_by(username=username).first()
    if user.role==RoleEnum.INFLUENCER:
        flash('Access denied.', 'danger')
        return redirect(url_for('home'))
    campaigns = Campaign.query.all()
    return render_template('campaigns.html', campaigns=campaigns)

@app.route('/campaign/add', methods=['GET', 'POST'])
@login_required
def add_campaign():
    username=session['username']
    user = User.query.filter_by(username=username).first()
    if user.role!=RoleEnum.SPONSOR:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('home'))

    form = CampaignForm()
    if form.validate_on_submit():
        sponsor = Sponsor.query.filter_by(user_id=user.id).first()
        campaign = Campaign(
            sponsor_id=sponsor.id,
            name=form.name.data,
            description=form.description.data,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            budget=form.budget.data,
            visibility=form.visibility.data,
            goals=form.goals.data
        )
        db.session.add(campaign)
        db.session.commit()
        flash('Campaign added successfully.', 'success')
        return redirect(url_for('sponsor_home'))

    return render_template('add_campaign.html', form=form)

@app.route('/campaign/edit/<int:campaign_id>', methods=['GET', 'POST'])
@login_required
def edit_campaign(campaign_id):
    username=session['username']
    user = User.query.filter_by(username=username).first()
    campaign = Campaign.query.get_or_404(campaign_id)
    if user.role !=RoleEnum.SPONSOR or campaign.sponsor.user_id != user.id:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('index'))

    form = CampaignForm(obj=campaign)
    if form.validate_on_submit():
        campaign.name = form.name.data
        campaign.description = form.description.data
        campaign.start_date = form.start_date.data
        campaign.end_date = form.end_date.data
        campaign.budget = form.budget.data
        campaign.visibility = form.visibility.data
        campaign.goals = form.goals.data
        db.session.commit()
        flash('Campaign updated successfully.', 'success')
        return redirect(url_for('sponsor_home'))

    return render_template('edit_campaign.html', form=form, campaign=campaign)


@app.route('/campaign/delete/<int:campaign_id>', methods=['POST'])
@login_required
def delete_campaign(campaign_id):
    username=session['username']
    user = User.query.filter_by(username=username).first()
    campaign = Campaign.query.get_or_404(campaign_id)
    if user.role !=RoleEnum.SPONSOR or campaign.sponsor.user_id != user.id:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('index'))

    db.session.delete(campaign)
    db.session.commit()
    flash('Campaign deleted successfully.', 'success')
    return redirect(url_for('sponsor_home'))


@app.route('/stats')
@login_required
def stats():
    username=session['username']
    user = User.query.filter_by(username=username).first()
    if user.role ==RoleEnum.INFLUENCER:
        flash('Access denied.', 'danger')
        return redirect(url_for('index'))

    total_campaigns = Campaign.query.count()
    active_campaigns = Campaign.query.filter_by(is_active=True).count()
    influencers_involved = db.session.query(Campaign.influencers).distinct().count()
    campaigns = Campaign.query.all()

    campaign_progress = [{'title': campaign.name, 'progress': campaign.progress} for campaign in campaigns]

    return render_template('stats.html', 
                           total_campaigns=total_campaigns,
                           active_campaigns=active_campaigns,
                           influencers_involved=influencers_involved,
                           campaigns=campaign_progress)