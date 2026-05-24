"""
Database models for Rose Bot
Uses SQLAlchemy ORM with SQLite support
"""

import os
import threading
from sqlalchemy import create_engine, Column, Integer, BigInteger, String, Boolean, DateTime, Text, ForeignKey, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session, relationship
from sqlalchemy.sql import func
from bot.config import DATABASE_URL

# Handle PostgreSQL URL for Heroku/Railway
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

Base = declarative_base()

# Create engine
engine = create_engine(DATABASE_URL, pool_pre_ping=True, echo=False)

# Create session factory
Session = scoped_session(sessionmaker(bind=engine))

# Lock for thread safety
INSERTION_LOCK = threading.RLock()

class Chats(Base):
    __tablename__ = "chats"
    
    chat_id = Column(BigInteger, primary_key=True)
    chat_name = Column(String(255), nullable=True)
    chat_type = Column(String(20), default="supergroup")
    welcome_enabled = Column(Boolean, default=True)
    welcome_message = Column(Text, nullable=True)
    welcome_mute = Column(Boolean, default=False)
    welcome_mute_duration = Column(String(20), default="30m")
    goodbye_enabled = Column(Boolean, default=False)
    goodbye_message = Column(Text, nullable=True)
    rules = Column(Text, nullable=True)
    flood_limit = Column(Integer, default=3)
    flood_mode = Column(String(20), default="tmute")
    flood_action_duration = Column(String(20), default="1h")
    lock_url = Column(Boolean, default=False)
    lock_forward = Column(Boolean, default=False)
    lock_bot = Column(Boolean, default=False)
    lock_command = Column(Boolean, default=False)
    lock_contact = Column(Boolean, default=False)
    lock_location = Column(Boolean, default=False)
    lock_email = Column(Boolean, default=False)
    lock_phone = Column(Boolean, default=False)
    lock_game = Column(Boolean, default=False)
    lock_inline = Column(Boolean, default=False)
    lock_media = Column(Boolean, default=False)
    lock_sticker = Column(Boolean, default=False)
    lock_rtl = Column(Boolean, default=False)
    lock_arabic = Column(Boolean, default=False)
    lock_chinese = Column(Boolean, default=False)
    lock_japanese = Column(Boolean, default=False)
    lock_cyrillic = Column(Boolean, default=False)
    lock_warns = Column(Boolean, default=False)
    captcha_enabled = Column(Boolean, default=False)
    captcha_text = Column(String(255), default="Click the button to verify you're human")
    cleanwelcome = Column(Boolean, default=False)
    cleangoodbye = Column(Boolean, default=False)
    cleanservice = Column(Boolean, default=False)
    warn_limit = Column(Integer, default=3)
    warn_mode = Column(String(20), default="ban")
    warn_duration = Column(String(20), nullable=True)
    blacklist_mode = Column(String(20), default="warn")
    blacklist_action = Column(String(20), default="ban")
    disabled_commands = Column(Text, default="")
    connected_chat = Column(BigInteger, nullable=True)
    antiflood_enabled = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Users(Base):
    __tablename__ = "users"
    
    user_id = Column(BigInteger, primary_key=True)
    username = Column(String(100), nullable=True)
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    warns = Column(Integer, default=0)
    approved = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ChatMembers(Base):
    __tablename__ = "chat_members"
    
    id = Column(Integer, primary_key=True)
    chat_id = Column(BigInteger, ForeignKey('chats.chat_id'))
    user_id = Column(BigInteger, ForeignKey('users.user_id'))
    is_admin = Column(Boolean, default=False)
    is_owner = Column(Boolean, default=False)
    warnings = Column(Integer, default=0)
    approved = Column(Boolean, default=False)
    muted = Column(Boolean, default=False)
    muted_until = Column(DateTime(timezone=True), nullable=True)
    banned = Column(Boolean, default=False)
    banned_until = Column(DateTime(timezone=True), nullable=True)
    joined_at = Column(DateTime(timezone=True), server_default=func.now())
    
    chat = relationship("Chats")
    user = relationship("Users")

class Warnings(Base):
    __tablename__ = "warnings"
    
    id = Column(Integer, primary_key=True)
    chat_id = Column(BigInteger)
    user_id = Column(BigInteger)
    admin_id = Column(BigInteger)
    reason = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Filters(Base):
    __tablename__ = "filters"
    
    id = Column(Integer, primary_key=True)
    chat_id = Column(BigInteger)
    keyword = Column(String(100))
    response = Column(Text)
    is_sticker = Column(Boolean, default=False)
    is_document = Column(Boolean, default=False)
    is_image = Column(Boolean, default=False)
    is_audio = Column(Boolean, default=False)
    is_voice = Column(Boolean, default=False)
    is_video = Column(Boolean, default=False)
    created_by = Column(BigInteger)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (UniqueConstraint('chat_id', 'keyword', name='_chat_filter_uc'),)

class Notes(Base):
    __tablename__ = "notes"
    
    id = Column(Integer, primary_key=True)
    chat_id = Column(BigInteger)
    name = Column(String(100))
    value = Column(Text)
    file_id = Column(String(500), nullable=True)
    msg_type = Column(Integer, default=1)  # 1=text, 2=sticker, 3=document, 4=photo, 5=audio, 6=voice, 7=video
    created_by = Column(BigInteger)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (UniqueConstraint('chat_id', 'name', name='_chat_note_uc'),)

class Blacklist(Base):
    __tablename__ = "blacklist"
    
    id = Column(Integer, primary_key=True)
    chat_id = Column(BigInteger)
    trigger = Column(String(500))
    
    __table_args__ = (UniqueConstraint('chat_id', 'trigger', name='_chat_blacklist_uc'),)

class Federations(Base):
    __tablename__ = "federations"
    
    fed_id = Column(String(64), primary_key=True)
    owner_id = Column(BigInteger)
    fed_name = Column(String(255))
    fed_admins = Column(Text, default="")  # Comma-separated user IDs
    fed_bans = Column(Text, default="")  # JSON of banned users
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ChatFederations(Base):
    __tablename__ = "chat_federations"
    
    id = Column(Integer, primary_key=True)
    chat_id = Column(BigInteger, unique=True)
    fed_id = Column(String(64), ForeignKey('federations.fed_id'))

class WelcomeCaptcha(Base):
    __tablename__ = "welcome_captcha"
    
    id = Column(Integer, primary_key=True)
    chat_id = Column(BigInteger)
    user_id = Column(BigInteger)
    message_id = Column(BigInteger)
    captcha_message = Column(String(10))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Bans(Base):
    __tablename__ = "bans"
    
    id = Column(Integer, primary_key=True)
    chat_id = Column(BigInteger)
    user_id = Column(BigInteger)
    admin_id = Column(BigInteger)
    reason = Column(Text, nullable=True)
    ban_type = Column(String(20), default="ban")  # ban, mute, kick
    duration = Column(String(20), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ReportSettings(Base):
    __tablename__ = "report_settings"
    
    id = Column(Integer, primary_key=True)
    chat_id = Column(BigInteger, unique=True)
    enabled = Column(Boolean, default=True)

class Connections(Base):
    __tablename__ = "connections"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, unique=True)
    chat_id = Column(BigInteger)
    connected_at = Column(DateTime(timezone=True), server_default=func.now())

# Initialize database
def init_db():
    Base.metadata.create_all(engine)
    
# Get database session
def get_db():
    db = Session()
    try:
        return db
    finally:
        db.close()

# Chat operations
def get_chat(chat_id):
    db = get_db()
    return db.query(Chats).filter(Chats.chat_id == chat_id).first()

def add_chat(chat_id, chat_name=None, chat_type="supergroup"):
    with INSERTION_LOCK:
        db = get_db()
        chat = db.query(Chats).filter(Chats.chat_id == chat_id).first()
        if not chat:
            chat = Chats(chat_id=chat_id, chat_name=chat_name, chat_type=chat_type)
            db.add(chat)
            db.commit()
        return chat

def update_chat(chat_id, **kwargs):
    with INSERTION_LOCK:
        db = get_db()
        chat = db.query(Chats).filter(Chats.chat_id == chat_id).first()
        if chat:
            for key, value in kwargs.items():
                setattr(chat, key, value)
            db.commit()
        return chat

# User operations
def get_user(user_id):
    db = get_db()
    return db.query(Users).filter(Users.user_id == user_id).first()

def add_user(user_id, username=None, first_name=None, last_name=None):
    with INSERTION_LOCK:
        db = get_db()
        user = db.query(Users).filter(Users.user_id == user_id).first()
        if not user:
            user = Users(user_id=user_id, username=username, first_name=first_name, last_name=last_name)
            db.add(user)
            db.commit()
        return user

def update_user(user_id, **kwargs):
    with INSERTION_LOCK:
        db = get_db()
        user = db.query(Users).filter(Users.user_id == user_id).first()
        if user:
            for key, value in kwargs.items():
                setattr(user, key, value)
            db.commit()
        return user

# Initialize on import
init_db()
