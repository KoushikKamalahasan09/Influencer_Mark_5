from werkzeug.security import generate_password_hash
from flask_sqlalchemy import SQLAlchemy
from enum import Enum
from datetime import datetime
from main import app

db = SQLAlchemy(app)

class RoleEnum(Enum):
    ADMIN = 'admin'
    SPONSOR = 'sponsor'
    INFLUENCER = 'influencer'

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    passhash = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    role = db.Column(db.Enum(RoleEnum), nullable=False)  # Enum for role
    sponsor = db.relationship('Sponsor', backref='user', uselist=False)
    influencer = db.relationship('Influencer', backref='user', uselist=False)

# Sponsor model
class Sponsor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    company_name = db.Column(db.String(100))
    individual_name = db.Column(db.String(100))
    industry = db.Column(db.String(100))
    budget = db.Column(db.Float)
    campaigns = db.relationship('Campaign', backref='sponsor')

# Influencer model
class Influencer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(100))
    platform = db.Column(db.String(100))
    reach = db.Column(db.Integer)
    ad_requests = db.relationship('AdRequest', backref='influencer')
    campaigns = db.relationship('Campaign', secondary='campaign_influencer', backref='influencers')

# Campaign model
class Campaign(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sponsor_id = db.Column(db.Integer, db.ForeignKey('sponsor.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    start_date = db.Column(db.DateTime, default=datetime.now())
    end_date = db.Column(db.DateTime)
    budget = db.Column(db.Float)
    visibility = db.Column(db.String(50), default='public')  # 'public' or 'private'
    goals = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    progress = db.Column(db.Float, default=0.0)
    ad_requests = db.relationship('AdRequest', backref='campaign')

# Campaign-Influencer association table
campaign_influencer = db.Table('campaign_influencer',
    db.Column('campaign_id', db.Integer, db.ForeignKey('campaign.id'), primary_key=True),
    db.Column('influencer_id', db.Integer, db.ForeignKey('influencer.id'), primary_key=True)
)

# AdRequest model
class AdRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'), nullable=False)
    influencer_id = db.Column(db.Integer, db.ForeignKey('influencer.id'), nullable=False)
    messages = db.Column(db.Text)
    requirements = db.Column(db.Text)
    payment_amount = db.Column(db.Float)
    status = db.Column(db.String(50), default='Pending')  # 'Pending', 'Accepted', 'Rejected'

# Flag model (for inappropriate campaigns/users)
class Flag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'), nullable=True)
    reason = db.Column(db.Text)
    flagged_at = db.Column(db.DateTime, default=datetime.now())
    
class CampaignApplication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='pending')
    applied_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)





with app.app_context():
    db.create_all()
    admin = User.query.filter_by(role=RoleEnum.ADMIN).first()
    if not admin:
        passhash = generate_password_hash('admin')
        admin = User(username='admin', passhash=passhash, email='admin@example.com', role=RoleEnum.ADMIN)
        db.session.add(admin)
        db.session.commit()