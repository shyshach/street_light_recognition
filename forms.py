from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError


def my_length_check(form, field):
    if len(field.data) < 6:
        raise ValidationError('Password needs to be at least 6 characters')


class RegistrationForm(FlaskForm):
    phone = StringField('Phone', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password1 = PasswordField('Password', validators=[DataRequired(), my_length_check])
    password2 = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password1')])
    submit = SubmitField('Register')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')
