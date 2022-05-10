from wtforms import Form
from wtforms.validators import DataRequired, Length
from wtforms.fields import TextAreaField, HiddenField, StringField, SubmitField, EmailField, PasswordField
from flask_wtf.file import FileField

class LoginForm(Form):
    username = StringField(label='Brukernavn:', id='username_login', validators=[DataRequired(), Length(max=45)])
    password = PasswordField(label='Passord:', id='password_login', validators=[DataRequired(), Length(max=45)])
    submit_login = SubmitField('Logg inn')

class UserForm(Form):
    username = StringField('Brukernavn', validators=[DataRequired(), Length(max=45)])
    email = EmailField('Epost', validators=[DataRequired(), Length(max=320)])
    email_val = EmailField('Bekreft epost', validators=[DataRequired(), Length(max=320)])
    password = PasswordField('Passord', validators=[DataRequired(), Length(max=45)])
    password_val = PasswordField('Bekreft passord', validators=[DataRequired(), Length(max=45)])
    firstname = StringField('Fornavn', [DataRequired(), Length(max=45)])
    lastname = StringField('Etternavn', [DataRequired(), Length(max=45)])
    submit_reg = SubmitField('Registrer')
    

class ContentForm(Form):
    title = StringField('Tittel', validators= [DataRequired(), Length(max=45)])
    tags = StringField('Tags', validators= [DataRequired(), Length(max=200)])
    description = TextAreaField('Beskrivelse', validators= [DataRequired(), Length(max=500)])
    restriction = StringField('restriction', validators= [DataRequired()])
    
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
    submit_upload = SubmitField('Last opp')
    submit_edit = SubmitField('Rediger')

class CommentForm(Form):
    text = TextAreaField('Kommentar', validators= [DataRequired(), Length(max=500)])
    contentID = HiddenField()
    submit_comment = SubmitField('Kommenter')

