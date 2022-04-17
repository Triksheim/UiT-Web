from wtforms import Form
from wtforms.validators import DataRequired, Length
from wtforms.fields import StringField, SubmitField, EmailField, PasswordField

class UserForm(Form):
    username = StringField('Username', validators=[DataRequired(), Length(max=45)])
    email = EmailField('Email', validators=[DataRequired(), Length(max=45)])
    password = PasswordField('Password', validators=[DataRequired(), Length(max=45)])
    firstname = StringField('First Name', [DataRequired(), Length(max=45)])
    lastname = StringField('Last Name', [DataRequired(), Length(max=45)])

    submit = SubmitField('Registrer')
    