import os
from datetime import datetime
from flask import Flask, render_template, flash, request, redirect, url_for, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_migrate import Migrate
from dotenv import load_dotenv
from models import db, User, Bot, Chat, Message, RAGConfig
from forms import LoginForm, RegistrationForm, BotForm, MessageForm
from src.gpt_api import GPT_API

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev')
# Update database URL to use Docker service name
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@postgres/chatbot_platform')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Invalid email or password')
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first():
            flash('Email already registered')
            return render_template('register.html', form=form)
        
        user = User(email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(url_for('dashboard'))
    return render_template('register.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    # Get all global bots and user's personal bots
    bots = Bot.query.filter(
        (Bot.is_global == True) | (Bot.creator_id == current_user.id)
    ).all()
    return render_template('dashboard.html', bots=bots)

@app.route('/bot/new', methods=['GET', 'POST'])
@login_required
def create_bot():
    form = BotForm()
    if form.validate_on_submit():
        try:
            # Create bot
            bot = Bot(
                name=form.name.data,
                description=form.description.data,
                system_prompt=form.system_prompt.data,
                is_global=form.is_global.data,
                creator_id=current_user.id
            )
            db.session.add(bot)
            db.session.flush()  # Get bot.id without committing
            
            # Create RAG configuration
            rag_config = RAGConfig(
                bot_id=bot.id,
                vectorstore_path=form.vectorstore_path.data,
                prompt_template=form.prompt_template.data,
                model_name=form.model_name.data,
                temperature=form.temperature.data
            )
            db.session.add(rag_config)
            db.session.commit()
            
            flash('Bot created successfully!')
            return redirect(url_for('dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating bot: {str(e)}', 'error')
            return render_template('create_bot.html', form=form)
            
    return render_template('create_bot.html', form=form)

@app.route('/chat/<int:bot_id>')
@login_required
def chat(bot_id):
    bot = Bot.query.get_or_404(bot_id)
    if not bot.is_global and bot.creator_id != current_user.id:
        flash('You do not have access to this bot')
        return redirect(url_for('dashboard'))
    
    # Get or create chat
    chat = Chat.query.filter_by(user_id=current_user.id, bot_id=bot_id).first()
    if not chat:
        chat = Chat(user_id=current_user.id, bot_id=bot_id)
        db.session.add(chat)
        db.session.commit()
    
    # Get last 15 messages
    messages = Message.query.filter_by(chat_id=chat.id).order_by(Message.timestamp.desc()).limit(15).all()
    messages.reverse()
    
    form = MessageForm()
    return render_template('chat.html', bot=bot, chat=chat, messages=messages, form=form)

@app.route('/chat/<int:chat_id>/message', methods=['POST'])
@login_required
def send_message(chat_id):
    chat = Chat.query.get_or_404(chat_id)
    if chat.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    form = MessageForm()
    if form.validate_on_submit():
        try:
            # Save user message
            user_message = Message(
                chat_id=chat_id,
                role='user',
                content=form.content.data
            )
            db.session.add(user_message)
            
            # Get bot's system prompt
            bot = Bot.query.get(chat.bot_id)
            
            # Get last 5 messages for context
            context_messages = Message.query.filter_by(chat_id=chat_id).order_by(Message.timestamp.desc()).limit(5).all()
            context_messages.reverse()
            
            # Format context messages
            context = "\n".join([f"{msg.role}: {msg.content}" for msg in context_messages])
            
            # Initialize GPT API and get response
            gpt_api = GPT_API(model="gpt-4o-mini", temperature=0.3)
            bot_response_text, cost = gpt_api.invoke(context)
            
            # Save bot's response
            bot_response = Message(
                chat_id=chat_id,
                role='assistant',
                content=bot_response_text
            )
            db.session.add(bot_response)
            db.session.commit()
            
            return jsonify({
                'user_message': {
                    'content': user_message.content,
                    'timestamp': user_message.timestamp.isoformat()
                },
                'bot_response': {
                    'content': bot_response.content,
                    'timestamp': bot_response.timestamp.isoformat()
                }
            })
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
    
    return jsonify({'error': 'Invalid message'}), 400

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', debug=True)
