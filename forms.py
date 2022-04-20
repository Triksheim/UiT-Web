from wtforms import Form
from wtforms.validators import DataRequired, Length, NumberRange
from wtforms.fields import TextAreaField, HiddenField, IntegerField, StringField, SubmitField, EmailField, PasswordField
from flask_wtf.file import FileField

class LoginForm(Form):
    username = StringField('Brukernavn:', validators=[DataRequired(), Length(max=45)])
    password = PasswordField('Passord:', validators=[DataRequired(), Length(max=45)])
    submit = SubmitField('Logg inn')

class UserForm(Form):
    username = StringField('Username', validators=[DataRequired(), Length(max=45)])
    email = EmailField('Email', validators=[DataRequired(), Length(max=45)])
    password = PasswordField('Password', validators=[DataRequired(), Length(max=45)])
    firstname = StringField('First Name', [DataRequired(), Length(max=45)])
    lastname = StringField('Last Name', [DataRequired(), Length(max=45)])

    submit = SubmitField('Registrer')
    

class ContentForm(Form):
    title = StringField('Tittel', validators= [DataRequired(), Length(max=45)])
    tags = StringField('Tags', validators= [DataRequired(), Length(max=200)])
    description = TextAreaField('Beskrivelse', validators= [DataRequired(), Length(max=500)])
    open = IntegerField('open', validators= [DataRequired(), NumberRange(min=1,max=2)])
    
    file = FileField('File')

    filename = HiddenField()
    filedata = HiddenField()
    filedata_base64 = HiddenField()
    mimetype = HiddenField()
    size = HiddenField()
    date = HiddenField()
    contentID = HiddenField()
    owner = HiddenField()

    submit_next = SubmitField('Neste')
    submit = SubmitField('Last opp')
    submit_edit = SubmitField('Rediger')

class CommentForm(Form):
    text = TextAreaField('Kommentar', validators= [DataRequired(), Length(max=500)])
    contentID = HiddenField()
    submit = SubmitField('Kommenter')

class SearchForm(Form):
    search_text = StringField('Search', validators=[DataRequired(), Length(max=45)])
    submit = SubmitField('Søk')
