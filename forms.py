from flask_wtf  import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import StringField, IntegerField, PasswordField, BooleanField, SelectField, TextAreaField
from wtforms.validators import InputRequired
from wtforms.fields import FieldList

class TranslateForm(FlaskForm):
    file = FileField('Word файл с данными: ', validators=[FileRequired()])
