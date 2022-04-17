from wtforms import Form
from wtforms.validators import DataRequired, Length, NumberRange
from wtforms.fields import TextAreaField, HiddenField, IntegerField, DateField, StringField, SubmitField
from flask_wtf.file import FileAllowed, FileField, FileRequired




class ContentForm(Form):
    
    
    
    title = StringField('Tittel', validators= [DataRequired(), Length(max=45)])
    tags = StringField('Tags', validators= [DataRequired(), Length(max=200)])
    description = TextAreaField('Beskrivelse', validators= [DataRequired(), Length(max=200)])
    open = IntegerField('open', validators= [DataRequired(), NumberRange(min=1,max=2)])
    
    file = FileField('File')

    filename = HiddenField()
    filedata = HiddenField()
    filedata_base64 = HiddenField()
    mimetype = HiddenField()
    size = HiddenField()
    date = HiddenField()

    submit_next = SubmitField('Neste')
    submit = SubmitField('Last opp')

