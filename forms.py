from flask_wtf  import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import StringField, IntegerField, PasswordField, BooleanField, SelectField, TextAreaField, SubmitField, FloatField
from wtforms.validators import InputRequired, DataRequired, Email, Length, EqualTo
from wtforms.fields import FieldList

class TranslateForm(FlaskForm):
    file = FileField('Word файл с данными: ', validators=[FileRequired()])

class RAGForm(FlaskForm):
    query = StringField('Ваш вопрос: ', validators=[InputRequired()])

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

class BotForm(FlaskForm):
    name = StringField('Bot Name', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description')
    system_prompt = TextAreaField('System Prompt', validators=[DataRequired()])
    is_global = BooleanField('Make Bot Global')
    
    # RAG Configuration fields
    vectorstore_path = StringField('Vectorstore Path', validators=[DataRequired()])
    prompt_template = TextAreaField('RAG Prompt Template', validators=[DataRequired()])
    model_name = StringField('Model Name', default="gpt-4o-mini")
    temperature = FloatField('Temperature', default=0.0)
    
    submit = SubmitField('Create Bot')

class MessageForm(FlaskForm):
    content = TextAreaField('Message', validators=[DataRequired()])
    submit = SubmitField('Send')