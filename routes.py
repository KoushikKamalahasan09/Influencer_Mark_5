from main import app
from flask import Flask, render_template, request, redirect, session, url_for, flash
from models import RoleEnum ,db, User, Sponsor, Influencer ,Campaign, AdRequest, Flag
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime
from forms import ProfileForm
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
    if user.role==RoleEnum.ADMIN:
        return redirect(url_for('admin'))
    elif user.role==RoleEnum.SPONSOR:
        return redirect(url_for('sponsor_home'))
    else:
        return redirect(url_for('influencer_home'))
    

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

@app.route('/users')
@admin_required
def user_list():
    users = User.query.all()
    return render_template('admin/users.html', users=users)

@app.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    query = request.form.get('search') if request.method == 'POST' else request.args.get('search')
    campaigns = []
    if query:
        campaigns = Campaign.query.filter(Campaign.title.ilike(f'%{query}%')).all()

    return render_template('search.html', query=query, campaigns=campaigns)


@app.route('/sponsor_register', methods=['POST'])
def register_post():
    email = request.form.get('email')
    username = request.form.get('username')
    password = request.form.get('password')
    confirm = request.form.get('confirm')

    # all not nullable inputs are not empty
    if not username or not password or not confirm or not email:
        flash("Please fill all the mandatory fields")
        return redirect(url_for('register'))

    # confirm and password should be same
    if not password == confirm:
        flash("Confirm and Password are not same")
        return redirect(url_for('register'))

    # username should be unique
    user = User.query.filter_by(username=username).first()
    if user:
        flash("Please choose another username, selected username is taken")
        return redirect(url_for('register'))


    passhash = generate_password_hash(password)

    user = User(email=email, username=username, passhash=passhash,role=RoleEnum.SPONSOR)
    db.session.add(user)
    db.session.commit()
    flash("Registration Successful, Please login to continue")
    return redirect(url_for('login'))

@app.route('/influencer_register', methods=['POST'])
def register_post():
    email = request.form.get('email')
    username = request.form.get('username')
    password = request.form.get('password')
    confirm = request.form.get('confirm')

    # all not nullable inputs are not empty
    if not username or not password or not confirm or not email:
        flash("Please fill all the mandatory fields")
        return redirect(url_for('register'))

    # confirm and password should be same
    if not password == confirm:
        flash("Confirm and Password are not same")
        return redirect(url_for('register'))

    # username should be unique
    user = User.query.filter_by(username=username).first()
    if user:
        flash("Please choose another username, selected username is taken")
        return redirect(url_for('register'))


    passhash = generate_password_hash(password)

    user = User(email=email, username=username, passhash=passhash,role=RoleEnum.INFLUENCER)
    db.session.add(user)
    db.session.commit()
    flash("Registration Successful, Please login to continue")
    return redirect(url_for('login'))


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    username=session['username']
    user = User.query.filter_by(username=username).first()
    form = ProfileForm(obj=user)

    if user.role ==RoleEnum.SPONSOR:
        form.company_name.data = user.sponsor.company_name
        form.individual_name.data = user.sponsor.individual_name
        form.industry.data = user.sponsor.industry

    elif user.role ==RoleEnum.INFLUENCER:
        form.name.data = user.influencer.name
        form.category.data = user.influencer.category
        form.niche.data = user.influencer.niche
        form.reach.data = user.influencer.reach

    return render_template('profile.html', form=form)    

@app.route('/profile/update', methods=['POST'])
@login_required
def update_profile():
    form = ProfileForm()
    username=session['username']
    user = User.query.filter_by(username=username).first()
    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data

        if form.password.data:
            user.passhash = generate_password_hash(form.password.data)

        if user.role ==RoleEnum.SPONSOR:
            user.sponsor.company_name = form.company_name.data
            user.sponsor.individual_name = form.individual_name.data
            user.sponsor.industry = form.industry.data

        elif user.role ==RoleEnum.INFLUENCER:
            user.influencer.name = form.name.data
            user.influencer.category = form.category.data
            user.influencer.niche = form.niche.data
            user.influencer.reach = form.reach.data

        db.session.commit()
        flash('Profile updated successfully.', 'success')
        return redirect(url_for('profile'))

    return render_template('profile.html', form=form)


@app.route('/home/influencer')
@login_required
def influencer_home():
    username=session['username']
    user = User.query.filter_by(username=username).first()
    
    if user.role!=RoleEnum.INFLUENCER:
        flash('Access denied.', 'danger')
        return redirect(url_for('home'))
    return render_template('influencer_home.html', user=user)

@app.route('/home/sponsor')
@login_required
def sponsor_home():
    username=session['username']
    user = User.query.filter_by(username=username).first()
    if user.role!=RoleEnum.SPONSOR:
        flash('Access denied.', 'danger')
        return redirect(url_for('home'))
    return render_template('sponsor_home.html', user=user)

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

@app.route('/campaigns/add', methods=['GET', 'POST'])
@login_required
def add_campaign():
    username=session['username']
    user = User.query.filter_by(username=username).first()
    if user.role != RoleEnum.SPONSOR:
        flash('Access denied.', 'danger')
        return redirect(url_for('home'))
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        # Add more fields as needed
        campaign = Campaign(name=title, description=description)
        db.session.add(campaign)
        db.session.commit()
        flash('Campaign added successfully', 'success')
        return redirect(url_for('campaigns'))
    return render_template('add_campaign.html')

@app.route('/campaigns/edit/<int:campaign_id>', methods=['GET', 'POST'])
@login_required
def edit_campaign(campaign_id):
    username=session['username']
    user = User.query.filter_by(username=username).first()
    if user.role != RoleEnum.SPONSOR:
        flash('Access denied.', 'danger')
        return redirect(url_for('home'))
    campaign = Campaign.query.get_or_404(campaign_id)
    if request.method == 'POST':
        campaign.name = request.form['title']
        campaign.description = request.form['description']
        # Update more fields as needed
        db.session.commit()
        flash('Campaign updated successfully', 'success')
        return redirect(url_for('campaigns'))
    return render_template('edit_campaign.html', campaign=campaign)

@app.route('/campaigns/delete/<int:campaign_id>', methods=['POST'])
@login_required
def delete_campaign(campaign_id):
    username=session['username']
    user = User.query.filter_by(username=username).first()
    if user.role ==RoleEnum.INFLUENCER:
        flash('Access denied.', 'danger')
        return redirect(url_for('index'))
    campaign = Campaign.query.get_or_404(campaign_id)
    db.session.delete(campaign)
    db.session.commit()
    flash('Campaign deleted successfully', 'success')
    return redirect(url_for('campaigns'))


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
