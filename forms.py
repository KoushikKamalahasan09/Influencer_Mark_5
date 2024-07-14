from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField,TextAreaField, DateTimeField, FloatField, SelectField
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


class CampaignForm(FlaskForm):
    name = StringField('Campaign Name', validators=[DataRequired(), Length(min=2, max=100)])
    description = TextAreaField('Description', validators=[DataRequired()])
    start_date = DateTimeField('Start Date', validators=[DataRequired()], format='%Y-%m-%d %H:%M:%S')
    end_date = DateTimeField('End Date', validators=[DataRequired()], format='%Y-%m-%d %H:%M:%S')
    budget = FloatField('Budget', validators=[DataRequired()])
    visibility = SelectField('Visibility', choices=[('public', 'Public'), ('private', 'Private')], validators=[DataRequired()])
    goals = TextAreaField('Goals', validators=[DataRequired()])
    submit = SubmitField('Submit')
