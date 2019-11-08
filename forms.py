from wtforms import Form, BooleanField, StringField, PasswordField, validators, TextAreaField, RadioField
from wtforms.validators import ValidationError

class SignupForm(Form):
    username = StringField('Username', [validators.Length(min=3, max=25),validators.DataRequired()],render_kw={"placeholder": "Enter your name..."})
    email = StringField('Email Address', [validators.Length(min=6, max=35),validators.DataRequired()],render_kw={"placeholder": "Enter your email..."})
    password = PasswordField('Password',[
        validators.DataRequired(),
        validators.EqualTo('confirmpassword',message='Your passwords do not match')
    ],render_kw={"placeholder": "Enter your password..."})
    confirmpassword = PasswordField('Confirm password',[validators.DataRequired()],render_kw={"placeholder": "Re-enter your password..."})

class LoginForm(Form):
    username = StringField('Username', [validators.Length(min=3, max=25)],
                           render_kw={"placeholder": "Enter your name..."})
    email = StringField('Email Address', [validators.Length(min=6, max=35), validators.DataRequired()],
                        render_kw={"placeholder": "Enter your email..."})
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirmpassword', message='Your passwords do not match')
    ], render_kw={"placeholder": "Enter your password..."})