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
        if not user.is_admin:
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
        return render_template('sponsor_home.html',user=user)
    else:
        return render_template('influencer_home.html',user=user)
    
@app.route('/profile')
@login_required
def profile():
    username=session['username']
    user = User.query.filter_by(username=username).first()
    return render_template('profile.html', user=user)

@app.route('/profile', methods=['POST'])
@login_required
def profile_post():
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
    return render_template('admin.html', users=users)

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