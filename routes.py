from main import app
from flask import Flask, render_template, request, redirect, session, url_for, flash,make_response
from models import RoleEnum ,db, User, Sponsor, Influencer ,Campaign,CampaignApplication
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import inch

import io
from datetime import datetime
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
    session['role']=user.role.value
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
    username = session['username']
    user = User.query.filter_by(username=username).first()
    return render_template('admin_home.html',user=user)

@app.route('/admin/users')
@admin_required
def list_users():
    users = User.query.all()
    return render_template('list_users.html', users=users,RoleEnum=RoleEnum)

@app.route('/admin/users/delete/<int:user_id>', methods=['POST'])
@admin_required
def delete_user(user_id):
    user_to_delete = User.query.get_or_404(user_id)
    if user_to_delete.role == RoleEnum.ADMIN:
        flash('Admin accounts cannot be deleted.', 'danger')
        return redirect(url_for('list_users'))
    db.session.delete(user_to_delete)
    db.session.commit()
    flash('User has been deleted.', 'success')
    return redirect(url_for('list_users'))

@app.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    query = request.form.get('search') if request.method == 'POST' else request.args.get('search')
    campaigns = []
    if query:
        campaigns = Campaign.query.filter(Campaign.name.ilike(f'%{query}%')).all()

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
    else:
        return render_template('profile_admin.html',user=user)    

@app.route('/profile/update')
@login_required
def update_profile():
    username = session['username']
    user = User.query.filter_by(username=username).first()
    
    if user.role==RoleEnum.SPONSOR:
        sponsor = Sponsor.query.filter_by(user_id=user.id).first()
        return render_template('update_sponsor.html',user=user,sponsor=sponsor)
    elif user.role==RoleEnum.INFLUENCER:
        influencer = Influencer.query.filter_by(user_id=user.id).first()    
        return render_template('update_influencer.html',user=user,influencer=influencer)  
    else:
        return render_template('update_admin.html',user=user) 
        

@app.route('/profile/update',methods=['POST'])
@login_required
def update_post():
    username = session['username']
    user = User.query.filter_by(username=username).first()
    if user.role==RoleEnum.SPONSOR:
        sponsor = Sponsor.query.filter_by(user_id=user.id).first()
        nusername = request.form.get('username')
        password = request.form.get('password')
        npassword = request.form.get('npassword')
        email=request.form.get('email')
        company_name = request.form.get('company_name')
        individual_name = request.form.get('individual_name')
        budget = request.form.get('budget')
        industry=request.form.get('industry')
        
        if password != "" and npassword != "":
            if check_password_hash(user.passhash, password):
                user.passhash = generate_password_hash(npassword)
                flash("Password changed successfully")
            else:
                flash("Entered current password is incorrect")

        if nusername != user.username and nusername != "":
            quser = User.query.filter_by(username=nusername).first()
            if quser:
                flash("Username is already taken, please choose any other username")
                return redirect(url_for('update_profile'))
        if email != user.email and email != "":
            quser = User.query.filter_by(email=email).first()
            if quser:
                flash("Email is already in use.")
                return redirect(url_for('update_profile'))
        
        
        user.username = nusername
        user.email = email
        sponsor.comapny_name = company_name
        sponsor.individual_name = individual_name
        sponsor.budget = budget
        sponsor.industry = industry
            
        session['username']=nusername
        flash(f"The entered changes have been noted and changed in our side.",category='success')
    
    elif user.role==RoleEnum.INFLUENCER:
        influencer = Influencer.query.filter_by(user_id=user.id).first()
        nusername = request.form.get('username')
        password = request.form.get('password')
        npassword = request.form.get('npassword')
        email=request.form.get('email')
        name = request.form.get('name')
        category = request.form.get('category')
        platform = request.form.get('platform')
        reach=request.form.get('reach')
        
        if password != "" and npassword != "":
            if check_password_hash(user.passhash, password):
                user.passhash = generate_password_hash(npassword)
                flash("Password changed successfully")
            else:
                flash("Entered current password is incorrect")

        if nusername != user.username and nusername != "":
            quser = User.query.filter_by(username=nusername).first()
            if quser:
                flash("Username is already taken, please choose any other username")
                return redirect(url_for('update_profile'))
        if email != user.email and email != "":
            quser = User.query.filter_by(email=email).first()
            if quser:
                flash("Email is already in use.")
                return redirect(url_for('update_profile'))
        
        
        user.username = nusername
        user.email = email
        influencer.name = name
        influencer.category = category
        influencer.platform = platform
        influencer.reach = reach
            
        session['username']=nusername
        flash(f"The entered changes have been noted and changed in our side.",category='success')
        
    else:
        nusername = request.form.get('username')
        password = request.form.get('password')
        npassword = request.form.get('npassword')
        email=request.form.get('email')
        
        if password != "" and npassword != "":
            if check_password_hash(user.passhash, password):
                user.passhash = generate_password_hash(npassword)
                flash("Password changed successfully")
            else:
                flash("Entered current password is incorrect")

        if nusername != user.username and nusername != "":
            quser = User.query.filter_by(username=nusername).first()
            if quser:
                flash("Username is already taken, please choose any other username")
                return redirect(url_for('update_profile'))
        if email != user.email and email != "":
            quser = User.query.filter_by(email=email).first()
            if quser:
                flash("Email is already in use.")
                return redirect(url_for('update_profile'))
        
        
        user.username = nusername
        user.email = email
        session['username']=nusername
        flash(f"The entered changes have been noted and changed in our side.",category='success')
        
    db.session.commit()
    return redirect(url_for('profile'))
    
    
@app.route('/influencer/home')
@login_required
def influencer_home():
    username = session['username']
    user = User.query.filter_by(username=username).first_or_404()
    
    if user.role != RoleEnum.INFLUENCER:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('index'))
    
    # Get all public campaigns
    campaigns = Campaign.query.filter_by(visibility='public').all()
    
    # Add the 'applied' status for each campaign
    applied_campaign_ids = {app.campaign_id for app in CampaignApplication.query.filter_by(user_id=user.id).all()}
    
    for campaign in campaigns:
        campaign.applied = campaign.id in applied_campaign_ids
    
    return render_template('influencer_home.html', campaigns=campaigns, user=user)

@app.route('/profile/delete/confirmation')
@login_required
def delete_profile_confirmation():
    username = session['username']
    user = User.query.filter_by(username=username).first()
    return render_template('delete_profile_confirmation.html', user=user)

@app.route('/sponsor/delete/confirmation')
@login_required
def delete_sponsor_confirmation():
    username = session['username']
    user = User.query.filter_by(username=username).first()
    return render_template('delete_sponsor_confirmation.html', user=user)


@app.route('/profile/delete', methods=['POST'])
@login_required
def delete_profile():
    username = session['username']
    user = User.query.filter_by(username=username).first()
    
    if user.role == RoleEnum.INFLUENCER:
        # Delete campaign applications
        CampaignApplication.query.filter_by(user_id=user.id).delete()
        
        # Delete influencer profile
        influencer = Influencer.query.filter_by(user_id=user.id).first()
        db.session.delete(influencer)
        
    elif user.role==RoleEnum.ADMIN:
        flash('Admin accounts cannot be deleted.', 'danger')
        return redirect(url_for('home'))
    
    else:
        sponsor=Sponsor.query.filter_by(user_id=user.id).first()
        Campaign.query.filter_by(sponsor_id=sponsor.id).delete()
        sponsor = Sponsor.query.filter_by(user_id=user.id).first()
        db.session.delete(sponsor)
    
    # Delete user account
    db.session.delete(user)
    db.session.commit()
    
    session.clear()
    flash('Your account has been deleted.', 'success')
    return redirect(url_for('home'))



@app.route('/sponsor/home')
@login_required
def sponsor_home():
    username=session['username']
    user = User.query.filter_by(username=username).first()
    if user.role !=RoleEnum.SPONSOR:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('home'))

    sponsor = Sponsor.query.filter_by(user_id=user.id).first()
    campaigns = Campaign.query.filter_by(sponsor_id=sponsor.id).all()

    return render_template('sponsor_home.html',campaigns=campaigns,user=user)

@app.route('/campaigns')
@login_required
def campaigns():
    username=session['username']
    user = User.query.filter_by(username=username).first()
    if user.role==RoleEnum.INFLUENCER:
        flash('Access denied.', 'danger')
        return redirect(url_for('home'))
    campaigns = Campaign.query.all()
    return render_template('campaigns.html', campaigns=campaigns,RoleEnum=RoleEnum,user=user)

@app.route('/campaign/add')
@login_required
def campaign_add():
    username=session['username']
    user=User.query.filter_by(username=username).first()
    if user.role != RoleEnum.SPONSOR:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('home'))
    return render_template('add_campaign.html')


@app.route('/campaign/add', methods=['POST'])
@login_required
def add_campaign():
    username = session['username']
    user = User.query.filter_by(username=username).first()
    if user.role != RoleEnum.SPONSOR:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('home'))

    sponsor = Sponsor.query.filter_by(user_id=user.id).first()
    sponsor_id=sponsor.id
    name = request.form.get('name')
    description = request.form.get('description')
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')
    budget = request.form.get('budget')
    goals = request.form.get('goals')
    visibility = request.form.get('visibility')
    
    if not name:
        flash("Name is mandatory")
        return redirect(url_for('campaign_add'))
    
    campaign = Campaign.query.filter_by(name=name).first()
    if campaign:
        flash("Campaign with this name already exists")
        return redirect(url_for('campaign_add'))

    if len(name) > 15:
        flash("Campaign Name cannot be more than 15 characters")
        return redirect(url_for('campaign_add'))

    if len(description) > 250:
        flash("Campaign Description cannot be more than 250 characters")
        return redirect(url_for('campaign_add'))
    
    if len(goals) > 50:
        flash("Campaign goals cannot be more than 50 characters")
        return redirect(url_for('campaign_add'))
    
    # Parse the start_date and end_date
    try:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    except ValueError:
        flash("Invalid date format")
        return redirect(url_for('campaign_add'))
    
    campaign = Campaign(sponsor_id=sponsor_id,name=name, description=description, start_date=start_date, end_date=end_date, budget=budget, goals=goals, visibility=visibility)
    db.session.add(campaign)
    db.session.commit()
    flash("Campaign added Successfully", category='success')
    return redirect(url_for('campaigns'))


@app.route('/category/<int:id>/edit')
@login_required
def campaign_edit(id):
    username=session['username']
    user = User.query.filter_by(username=username).first()
    if user.role!=RoleEnum.SPONSOR:
            flash('Unauthorized access.', 'danger')
            return redirect(url_for('home'))
    campaign = Campaign.query.get(id)
    return render_template('edit_campaign.html', campaign=campaign)


@app.route('/category/<int:id>/edit', methods=['POST'])
@admin_required
def category_edit_post(id):
    name = request.form.get('name')
    description = request.form.get('description')
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')
    budget = request.form.get('budget')
    goals = request.form.get('goals')
    visibility=request.form.get('visibility')

    if not name:
        flash("Name is mandatory")
        return redirect(url_for('campaigns'))

    current_campaign = Campaign.query.get(id)
    campaign = Campaign.query.filter_by(name=name).first()

    if campaign and campaign.id != current_campaign.id:
        flash("Campaign with this name already exists")
        return redirect(url_for('campaigns'))

    if len(name) > 15:
        flash("Category Name cannot be more than 15 characters")
        return redirect(url_for('campaign_edit'))

    if len(description) > 250:
        flash("Category Description cannot be more than 250 characters")
        return redirect(url_for('camapign_edit'))
    
    current_campaign.name = name
    current_campaign.description = description
    current_campaign.start_date = start_date
    current_campaign.end_date = end_date
    current_campaign.budget = budget
    current_campaign.goals = goals
    current_campaign.visibility = visibility
    db.session.commit()
    flash("Campaign edited Successfully")
    return redirect(url_for('campaigns'))

@app.route('/campaign/delete/<int:campaign_id>', methods=['POST'])
@login_required
def delete_campaign(campaign_id):
    username=session['username']
    user = User.query.filter_by(username=username).first()
    campaign = Campaign.query.get_or_404(campaign_id)
    if user.role !=RoleEnum.SPONSOR or campaign.sponsor.user_id != user.id:
        if user.role!=RoleEnum.ADMIN:
            
            flash('Unauthorized access.', 'danger')
            return redirect(url_for('home'))

    db.session.delete(campaign)
    db.session.commit()
    flash('Campaign deleted successfully.', 'success')
    return redirect(url_for('campaigns'))


@app.route('/stats')
@login_required
def stats():
    username = session['username']
    user = User.query.filter_by(username=username).first()

    if user.role == RoleEnum.INFLUENCER:
        campaigns = Campaign.query.join(CampaignApplication).filter(CampaignApplication.user_id == user.id).all()
    elif user.role == RoleEnum.SPONSOR:
        sponsor = Sponsor.query.filter_by(user_id=user.id).first()
        campaigns = Campaign.query.filter_by(sponsor_id=sponsor.id).all()
    else:  # Admin
        campaigns = Campaign.query.all()

    total_campaigns = len(campaigns)
    active_campaigns = len([campaign for campaign in campaigns if campaign.is_active])
    influencers_involved = len(set(influencer.id for campaign in campaigns for influencer in campaign.influencers))

    campaign_progress = [{'title': campaign.name, 'progress': campaign.progress} for campaign in campaigns]

    return render_template('stats.html', 
                           total_campaigns=total_campaigns,
                           active_campaigns=active_campaigns,
                           influencers_involved=influencers_involved,
                           campaigns=campaign_progress,
                           user_role=user.role)
    

@app.route('/apply_campaign/<int:campaign_id>', methods=['POST'])
@login_required
def apply_campaign(campaign_id):
    username = session['username']
    user = User.query.filter_by(username=username).first()
    campaign = Campaign.query.get_or_404(campaign_id)
    
    # Check if the user has already applied to the campaign
    existing_application = CampaignApplication.query.filter_by(user_id=user.id, campaign_id=campaign.id).first()
    if existing_application:
        flash('You have already applied for this campaign.', 'warning')
        return redirect(url_for('view_campaign', campaign_id=campaign.id))
    
    # Create a new CampaignApplication
    application = CampaignApplication(user_id=user.id, campaign_id=campaign.id)
    db.session.add(application)
    db.session.commit()
    
    flash('You have applied for the campaign!', 'success')
    return redirect(url_for('view_campaign', campaign_id=campaign.id))


@app.route('/campaign/<int:campaign_id>')
@login_required
def view_campaign(campaign_id):
    username = session['username']
    user = User.query.filter_by(username=username).first_or_404()
    campaign = Campaign.query.get_or_404(campaign_id)
    
    # Check if the user has applied for the campaign
    application = CampaignApplication.query.filter_by(user_id=user.id, campaign_id=campaign.id).first()

    # Determine if the user is an influencer and has applied for the campaign
    applied_campaign_ids = [app.campaign_id for app in CampaignApplication.query.filter_by(user_id=user.id).all()]
    
    return render_template('view_campaign.html', 
                           campaign=campaign, 
                           application=application,
                           user=user,
                           applied_campaign_ids=applied_campaign_ids,RoleEnum=RoleEnum)


@app.route('/unapply_campaign/<int:campaign_id>', methods=['POST'])
@login_required
def unapply_campaign(campaign_id):
    username = session['username']
    user = User.query.filter_by(username=username).first()
    campaign = Campaign.query.get_or_404(campaign_id)

    # Find the existing application to delete
    application = CampaignApplication.query.filter_by(user_id=user.id, campaign_id=campaign.id).first()

    if application:
        db.session.delete(application)  # Remove the application
        db.session.commit()  # Commit the change
        flash('You have successfully removed your application for this campaign!', 'success')
    else:
        flash('You have not applied for this campaign.')

    return redirect(url_for('view_campaign', campaign_id=campaign.id))
    

@app.route('/campaign/<int:campaign_id>', methods=['GET', 'POST'])
@login_required
def views_campaign(campaign_id):
    # Fetch the campaign by ID
    campaign = Campaign.query.get_or_404(campaign_id)
    
    # Get the username from the session
    username = session.get('username')
    user = User.query.filter_by(username=username).first_or_404()
    
    # Check if the user is an influencer
    if user.role != RoleEnum.INFLUENCER:
        flash('Access denied.', 'danger')
        return redirect(url_for('home'))

    # Check if the influencer has applied for this campaign
    influencer_campaign = CampaignApplication.query.filter_by(user_id=user.id, campaign_id=campaign_id).first()
    
    if not influencer_campaign:
        flash('You have not applied to this campaign.', 'danger')
        return redirect(url_for('home'))
    
    # Handle form submission to update progress
    if request.method == 'POST':
        progress = request.form.get('progress', type=int)
        if progress is not None and 0 <= progress <= 100:
            campaign.progress = progress
            db.session.commit()
            flash('Campaign progress updated successfully!', 'success')
        else:
            flash('Invalid progress value. Must be between 0 and 100.', 'danger')
    
    return render_template('view_campaign.html', campaign=campaign)

@app.route('/update_progress/<int:campaign_id>', methods=['POST'])
@login_required
def update_progress(campaign_id):
    username = session['username']
    user = User.query.filter_by(username=username).first_or_404()
    
    # Check if user is an influencer
    if user.role != RoleEnum.INFLUENCER:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('index'))
    
    # Get the campaign and check if the user has applied
    campaign = Campaign.query.get_or_404(campaign_id)
    application = CampaignApplication.query.filter_by(user_id=user.id, campaign_id=campaign_id).first()
    
    if not application:
        flash('You have not applied for this campaign.', 'danger')
        return redirect(url_for('influencer_home'))
    
    # Get the new progress value from the form
    new_progress = request.form.get('progress', type=float)
    
    if new_progress is not None and 0 <= new_progress <= 100:
        campaign.progress = new_progress
        db.session.commit()
        if campaign.progress == 100:
            return redirect(url_for('payment_page', campaign_id=campaign.id))
        flash('Progress updated successfully!', 'success')
    else:
        flash('Invalid progress value.', 'danger')
    
    return redirect(url_for('view_campaign', campaign_id=campaign_id))

@app.route('/payment/<int:campaign_id>')
@login_required
def payment_page(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    sponsor = User.query.get_or_404(campaign.sponsor_id)
    influencer = CampaignApplication.query.filter_by(campaign_id=campaign.id).first()
    return render_template('payment.html', campaign=campaign, sponsor=sponsor, influencer=influencer)


@app.route('/payment/<int:campaign_id>/generate_bill')
@login_required
def generate_bill(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    sponsor = Sponsor.query.get_or_404(campaign.sponsor_id)
    campaignapp = CampaignApplication.query.filter_by(campaign_id=campaign.id).first()
    influencer = Influencer.query.filter_by(user_id=campaignapp.user_id).first()
    
    # Create a file-like buffer to receive PDF data.
    buffer = io.BytesIO()

    # Create the PDF object, using the buffer as its "file."
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Add a title
    p.setFont("Helvetica-Bold", 16)
    p.drawString(1 * inch, 10 * inch, "Campaign Bill")

    # Draw a line below the title
    p.setLineWidth(1)
    p.line(1 * inch, 9.8 * inch, 7.5 * inch, 9.8 * inch)

    # Add campaign details
    p.setFont("Helvetica", 12)
    p.drawString(1 * inch, 9.5 * inch, f"Campaign: {campaign.name}")
    p.drawString(1 * inch, 9.2 * inch, f"Sponsor: {sponsor.company_name}")
    p.drawString(1 * inch, 8.9 * inch, f"Influencer: {influencer.name}")
    p.drawString(1 * inch, 8.6 * inch, f"Budget: ${campaign.budget}")
    p.drawString(1 * inch, 8.3 * inch, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Draw a line below the details
    p.setLineWidth(0.5)
    p.line(1 * inch, 8 * inch, 7.5 * inch, 8 * inch)

    # Add a footer
    p.setFont("Helvetica-Oblique", 10)
    p.setFillColor(colors.grey)
    p.drawString(1 * inch, 0.75 * inch, "Thank you for your business!")
    p.drawString(1 * inch, 0.5 * inch, "For any queries, contact support@example.com")

    # Close the PDF object cleanly.
    p.showPage()
    p.save()

    # Get the value of the BytesIO buffer and write it to the response.
    buffer.seek(0)
    pdf = buffer.getvalue()
    buffer.close()

    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=bill_{campaign.id}.pdf'
    
    return response
@app.route('/payment/<int:campaign_id>/complete', methods=['POST'])
@login_required
def complete_payment(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    
    # Delete campaign applications first
    CampaignApplication.query.filter_by(campaign_id=campaign.id).delete()
    
    # Delete the campaign
    db.session.delete(campaign)
    db.session.commit()
    
    flash('Payment completed and campaign deleted.', 'success')
    return redirect(url_for('influencer_home'))
