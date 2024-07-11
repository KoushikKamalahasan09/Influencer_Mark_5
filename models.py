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
    password = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    role = db.Column(db.Enum(RoleEnum), nullable=False)  # Enum for role

# Sponsor model
class Sponsor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    company_name = db.Column(db.String(100))
    individual_name = db.Column(db.String(100))
    industry = db.Column(db.String(100))
    budget = db.Column(db.Float)

# Influencer model
class Influencer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(100))
    niche = db.Column(db.String(100))
    reach = db.Column(db.Integer)

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
    
with app.app_context():
    db.create_all()
    admin = User.query.filter_by(role='admin').first()
    if not admin:
        passhash=generate_password_hash('admin')
        admin = User(username='admin', passhash=passhash, name='Admin', is_admin=True)
        db.session.add(admin)
        db.session.commit()