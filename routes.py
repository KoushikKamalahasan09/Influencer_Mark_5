from main import app
from flask import Flask, render_template, request, redirect, session, url_for, flash
from models import RoleEnum ,db, User, Sponsor, Influencer ,Campaign, AdRequest, Flag
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
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

@app.route('/search')
@login_required
def search():
    query = request.args.get('search')
    Campaigns = None
    if query:
        Campaigns = Campaign.query.filter(Campaign.name.ilike(f'%{query}%')).all()

    return render_template('search.html', query=query, Campaigns=Campaigns)

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
    if request.method == 'POST':
        nusername = request.form.get('username')
        password = request.form.get('password')
        npassword = request.form.get('npassword')
        username=session['username']
        user = User.query.filter_by(username=username).first()
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
                return redirect(url_for('profile'))
            user.username = nusername
            session['username']=nusername
            flash(f"Username changed to {nusername}")

        db.session.commit()
        return redirect(url_for('profile'))
    else:
        username=session['username']
        user = User.query.filter_by(username=username).first()
        return render_template('profile.html', user=user)
    

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