from wtforms import Form
from wtforms.validators import DataRequired, Length, NumberRange
from wtforms.fields import TextAreaField, HiddenField, IntegerField, DateField, StringField, SubmitField


class CommentForm(Form):
    text = TextAreaField('Kommentar', validators= [DataRequired(), Length(max=500)])
    contentID = HiddenField()
    submit = SubmitField('Kommenter')