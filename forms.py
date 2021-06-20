from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, PasswordField, SubmitField, IntegerField, FloatField
from wtforms.validators import DataRequired, Email, Length, EqualTo


class LoginForm(FlaskForm):
    email = StringField('Email: ', validators=[DataRequired(), Email(message="Enter a valid Email.")])
    password = PasswordField("Password: ", validators=[DataRequired(), Length(min=8, max=25, message="Password must be between 8-25 characters.")])
    login_button = SubmitField("Login")


class RegisterForm(FlaskForm):
    name = StringField("Name: ", validators=[DataRequired()])
    email = StringField("Email: ", validators=[DataRequired(), Email(message="Enter a valid Email. ")])
    password = PasswordField("Password: ", validators=[DataRequired(), EqualTo(fieldname="confirm_password", message="Passwords Must Match")])
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired(), Length(min=8, max=25, message="Password must be between 8-25 characters.")])
    register_button = SubmitField("Register")


class ItemForm(FlaskForm):
    name = StringField("Item Name or Description", validators=[DataRequired()])
    sex = StringField("Gender", validators=[DataRequired()])
    type = StringField("Type", validators=[DataRequired()])
    price = FloatField("Price", validators=[DataRequired()])
    supply = IntegerField("How many on stocks?", validators=[DataRequired()])
    size = StringField("Size(XXS/XS/S/M/L/XL/XXl)", validators=[DataRequired()])
    photo = FileField("Add an image", validators=[FileRequired(), FileAllowed(["jpg", "png", "jpeg"], "Images Only!")])
    submit = SubmitField("Submit")
