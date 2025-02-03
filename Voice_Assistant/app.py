from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import requests
import logging
import os
from datetime import datetime
from dotenv import load_dotenv
import speech_recognition as sr
from gtts import gTTS
import base64
import tempfile
import io
import json
import uuid

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///chat.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    chats = db.relationship('Chat', backref='user', lazy=True)
    preferences = db.relationship('UserPreference', backref='user', uselist=False)

class Chat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    messages = db.relationship('Message', backref='chat', lazy=True)
    is_favorite = db.Column(db.Boolean, default=False)
    category = db.Column(db.String(50))

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.Integer, db.ForeignKey('chat.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'user' or 'assistant'
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    is_voice = db.Column(db.Boolean, default=False)

class UserPreference(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    theme = db.Column(db.String(20), default='dark')
    voice_response = db.Column(db.Boolean, default=False)
    language = db.Column(db.String(10), default='en')
    notification_enabled = db.Column(db.Boolean, default=True)
    model_preference = db.Column(db.String(50), default='mistral-small')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# API Configuration
API_KEY = os.getenv('MISTRAL_API_KEY')
API_URL = os.getenv('MISTRAL_API_URL', 'https://api.mistral.ai/v1/chat/completions')

# Routes for Authentication
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.get_json()
        
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'error': 'Username already exists'}), 400
            
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already exists'}), 400
            
        user = User(
            username=data['username'],
            email=data['email'],
            password_hash=generate_password_hash(data['password'])
        )
        
        # Create default preferences
        preferences = UserPreference(user=user)
        
        db.session.add(user)
        db.session.add(preferences)
        db.session.commit()
        
        return jsonify({'message': 'Registration successful'})
        
    return render_template('register.html')

# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         data = request.get_json()
#         user = User.query.filter_by(username=data['username']).first()
        
#         if user and check_password_hash(user.password_hash, data['password']):
#             login_user(user)
#             return jsonify({'message': 'Login successful'})
            
#         return jsonify({'error': 'Invalid credentials'}), 401
        
#     return render_template('login.html')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()
            user = User.query.filter_by(username=data['username']).first()
            
            if user and check_password_hash(user.password_hash, data['password']):
                login_user(user)
                return jsonify({'message': 'Login successful'})
            
            return jsonify({'error': 'Invalid username or password'}), 401
            
        return jsonify({'error': 'Content-Type must be application/json'}), 415
        
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# Chat Routes
@app.route('/')
@login_required
def home():
    return render_template('index.html', user=current_user)

@app.route('/api/chats', methods=['GET'])
@login_required
def get_chats():
    chats = Chat.query.filter_by(user_id=current_user.id).order_by(Chat.created_at.desc()).all()
    return jsonify([{
        'id': chat.id,
        'title': chat.title,
        'created_at': chat.created_at.isoformat(),
        'is_favorite': chat.is_favorite,
        'category': chat.category
    } for chat in chats])

@app.route('/api/chat/<int:chat_id>', methods=['GET'])
@login_required
def get_chat(chat_id):
    chat = Chat.query.get_or_404(chat_id)
    if chat.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
        
    messages = Message.query.filter_by(chat_id=chat_id).order_by(Message.timestamp).all()
    return jsonify({
        'chat': {
            'id': chat.id,
            'title': chat.title,
            'created_at': chat.created_at.isoformat(),
            'is_favorite': chat.is_favorite,
            'category': chat.category
        },
        'messages': [{
            'content': msg.content,
            'role': msg.role,
            'timestamp': msg.timestamp.isoformat(),
            'is_voice': msg.is_voice
        } for msg in messages]
    })

@app.route('/api/chat', methods=['POST'])
@login_required
def create_chat():
    try:
        data = request.get_json()
        user_input = data.get('message')
        chat_id = data.get('chat_id')
        
        if not chat_id:
            # Create new chat
            chat = Chat(
                user_id=current_user.id,
                title=user_input[:50] + "...",  # Use first 50 chars as title
                category=data.get('category', 'general')
            )
            db.session.add(chat)
            db.session.commit()
            chat_id = chat.id
        else:
            chat = Chat.query.get_or_404(chat_id)
            if chat.user_id != current_user.id:
                return jsonify({'error': 'Unauthorized'}), 403

        # Save user message
        user_message = Message(
            chat_id=chat_id,
            content=user_input,
            role='user',
            is_voice=data.get('type') == 'voice'
        )
        db.session.add(user_message)
        
        # Get chat history
        messages = Message.query.filter_by(chat_id=chat_id).order_by(Message.timestamp).all()
        conversation_history = [{'role': msg.role, 'content': msg.content} for msg in messages]
        
        # Call AI API
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": current_user.preferences.model_preference,
            "messages": conversation_history[-5:]
        }
        
        response = requests.post(API_URL, json=payload, headers=headers)
        response.raise_for_status()
        
        bot_response = response.json()['choices'][0]['message']['content']
        
        # Save bot message
        bot_message = Message(
            chat_id=chat_id,
            content=bot_response,
            role='assistant'
        )
        db.session.add(bot_message)
        db.session.commit()
        
        # Generate audio if needed
        audio_data = None
        if current_user.preferences.voice_response:
            audio_data = text_to_speech(bot_response) # type: ignore
        
        return jsonify({
            'reply': bot_response,
            'audio': audio_data,
            'chat_id': chat_id
        })
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error in chat: {str(e)}")
        return jsonify({'error': str(e)}), 500

# User Preferences Routes
@app.route('/api/preferences', methods=['GET', 'PUT'])
@login_required
def handle_preferences():
    if request.method == 'GET':
        return jsonify({
            'theme': current_user.preferences.theme,
            'voice_response': current_user.preferences.voice_response,
            'language': current_user.preferences.language,
            'notification_enabled': current_user.preferences.notification_enabled,
            'model_preference': current_user.preferences.model_preference
        })
    
    data = request.get_json()
    for key, value in data.items():
        if hasattr(current_user.preferences, key):
            setattr(current_user.preferences, key, value)
    
    db.session.commit()
    return jsonify({'message': 'Preferences updated'})

# Chat Management Routes
@app.route('/api/chat/<int:chat_id>/favorite', methods=['POST'])
@login_required
def toggle_favorite(chat_id):
    chat = Chat.query.get_or_404(chat_id)
    if chat.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
        
    chat.is_favorite = not chat.is_favorite
    db.session.commit()
    return jsonify({'is_favorite': chat.is_favorite})

@app.route('/api/chat/<int:chat_id>', methods=['DELETE'])
@login_required
def delete_chat(chat_id):
    chat = Chat.query.get_or_404(chat_id)
    if chat.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
        
    db.session.delete(chat)
    db.session.commit()
    return jsonify({'message': 'Chat deleted'})

# Error Handlers
@app.errorhandler(404)
def not_found_error(error):
    return jsonify({'error': 'Resource not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
