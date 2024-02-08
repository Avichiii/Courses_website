from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField
from wtforms.validators import Length, EqualTo, Email, DataRequired, ValidationError, URL, NumberRange
from course.models import Users

class RegistrForm(FlaskForm):
    
    # will check if the user entered username is already present in the database
    def validate_username(self, username_to_check):
        #username_to_check is a form object thus we need to use .data to access the data
        name = Users.query.filter_by(username=username_to_check.data).first()
        
        # if name exist on the database, raise and error
        if name:
            raise ValidationError('User Name already Exists, Please Choose a Different Name')
    
    def validate_email(self, email_to_check):
        mail = Users.query.filter_by(email_address=email_to_check.data).first()
        
        if mail:
            raise ValidationError('Email Address already Exists, Please Choose a Different Email')
    
    username = StringField(label='User Name:', validators=[Length(min=4,max=30), DataRequired()])
    email = StringField(label='Email:', validators=[Email()])
    password = PasswordField(label='Password:', validators=[Length(min=8), DataRequired()])
    confirm_password = PasswordField(label='Confirm Password:', validators=[EqualTo('password'), DataRequired()])
    submit = SubmitField(label='Sign Up')


class LoginForm(FlaskForm):
    username = StringField(label='User Name:', validators=[DataRequired()])
    password = PasswordField(label='Password:', validators=[DataRequired()])
    submit = SubmitField(label='Sign In')


class GetLinkForm(FlaskForm):
    submit = SubmitField(label='Get Link')


class AddLinkForm(FlaskForm):
    # from /users route
    course_name = StringField(label='Course Name:', validators=[Length(min=3, max=30), DataRequired()])
    course_url = StringField(label='URL:', validators=[URL(), DataRequired()])
    token_worth = IntegerField(label='Token:', validators=[NumberRange(min=50, max=100), DataRequired()])
    description = StringField(label='Course Description:', validators=[Length(min=20), DataRequired()])
    submit = SubmitField(label='Add Course')


class AssignTokensForm(FlaskForm):
    username = StringField(label='User Name:', validators=[DataRequired()])
    token_count = IntegerField(label='Token:', validators=[DataRequired()])
    submit = SubmitField(label='Assign')