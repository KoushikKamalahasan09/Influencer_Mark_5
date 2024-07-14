from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length

class ProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[Length(min=6)])
    
    # Sponsor specific fields
    company_name = StringField('Company Name')
    individual_name = StringField('Individual Name')
    industry = StringField('Industry')

    # Influencer specific fields
    name = StringField('Name')
    category = StringField('Category')
    niche = StringField('Niche')
    reach = StringField('Reach')

    submit = SubmitField('Update')
