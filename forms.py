from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateTimeField, FloatField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length

class CampaignForm(FlaskForm):
    name = StringField('Campaign Name', validators=[DataRequired(), Length(min=2, max=100)])
    description = TextAreaField('Description', validators=[DataRequired()])
    start_date = DateTimeField('Start Date', validators=[DataRequired()], format='%Y-%m-%d %H:%M:%S')
    end_date = DateTimeField('End Date', validators=[DataRequired()], format='%Y-%m-%d %H:%M:%S')
    budget = FloatField('Budget', validators=[DataRequired()])
    visibility = SelectField('Visibility', choices=[('public', 'Public'), ('private', 'Private')], validators=[DataRequired()])
    goals = TextAreaField('Goals', validators=[DataRequired()])
    submit = SubmitField('Submit')
