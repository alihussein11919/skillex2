from datetime import datetime
from sqlalchemy import (
    create_engine, Column, Integer, String, Text, DateTime, Boolean,
    Enum, ForeignKey, DECIMAL, UniqueConstraint, Index
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

# --- Base Model Setup ---
Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    user_id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(100), nullable=False, unique=True)
    password = Column(String(255), nullable=False, default='default_password')
    role = Column(Enum('admin', 'teacher', 'student', name='user_roles'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user_skills = relationship('UserSkill', back_populates='user', cascade='all, delete-orphan')
    teacher = relationship('Teacher', uselist=False, back_populates='user', cascade='all, delete-orphan')
    student = relationship('Student', uselist=False, back_populates='user', cascade='all, delete-orphan')
    sent_messages = relationship('Message', foreign_keys='Message.sender_id', back_populates='sender', cascade='all, delete-orphan')
    received_messages = relationship('Message', foreign_keys='Message.receiver_id', back_populates='receiver', cascade='all, delete-orphan')
    reviews_given = relationship('Review', foreign_keys='Review.reviewer_id', back_populates='reviewer', cascade='all, delete-orphan')
    reviews_received = relationship('Review', foreign_keys='Review.reviewee_id', back_populates='reviewee', cascade='all, delete-orphan')
    admin_logs = relationship('AdminLog', back_populates='admin', cascade='all, delete-orphan')

class Skill(Base):
    __tablename__ = 'skills'
    skill_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False, unique=True)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    user_skills = relationship('UserSkill', back_populates='skill', cascade='all, delete-orphan')

class UserSkill(Base):
    __tablename__ = 'user_skills'
    __table_args__ = (UniqueConstraint('user_id', 'skill_id', name='unique_user_skill'),)
    user_skill_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    skill_id = Column(Integer, ForeignKey('skills.skill_id', ondelete='CASCADE'), nullable=False)
    proficiency_level = Column(Enum('beginner','intermediate','advanced','expert', name='proficiency_levels'), default='intermediate')
    user = relationship('User', back_populates='user_skills')
    skill = relationship('Skill', back_populates='user_skills')

class Teacher(Base):
    __tablename__ = 'teachers'
    teacher_id = Column(Integer, ForeignKey('users.user_id', ondelete='CASCADE'), primary_key=True)
    bio = Column(Text)
    hourly_rate = Column(DECIMAL(10,2), default=20.00)
    user = relationship('User', back_populates='teacher')
    lessons = relationship('Lesson', back_populates='teacher', cascade='all, delete-orphan')
    marketplace_products = relationship('MarketplaceProduct', back_populates='teacher', cascade='all, delete-orphan')
    matches = relationship('Match', back_populates='teacher', cascade='all, delete-orphan')

class Student(Base):
    __tablename__ = 'students'
    student_id = Column(Integer, ForeignKey('users.user_id', ondelete='CASCADE'), primary_key=True)
    learning_goals = Column(Text)
    user = relationship('User', back_populates='student')
    lessons = relationship('Lesson', back_populates='student', cascade='all, delete-orphan')
    orders = relationship('Order', back_populates='student', cascade='all, delete-orphan')
    matches = relationship('Match', back_populates='student', cascade='all, delete-orphan')

class Lesson(Base):
    __tablename__ = 'lessons'
    lesson_id = Column(Integer, primary_key=True, autoincrement=True)
    teacher_id = Column(Integer, ForeignKey('teachers.teacher_id', ondelete='CASCADE'), nullable=False)
    student_id = Column(Integer, ForeignKey('students.student_id', ondelete='CASCADE'), nullable=False)
    skill_id = Column(Integer, ForeignKey('skills.skill_id', ondelete='CASCADE'), nullable=False)
    scheduled_time = Column(DateTime, nullable=False)
    duration_minutes = Column(Integer, default=60, nullable=False)
    status = Column(Enum('scheduled','completed','canceled', name='lesson_statuses'), default='scheduled')
    price = Column(DECIMAL(10,2), nullable=False)
    teacher = relationship('Teacher', back_populates='lessons')
    student = relationship('Student', back_populates='lessons')
    skill = relationship('Skill')
    orders = relationship('Order', back_populates='lesson', cascade='all, delete-orphan')
    reviews = relationship('Review', back_populates='lesson', cascade='all, delete-orphan')

class Message(Base):
    __tablename__ = 'messages'
    message_id = Column(Integer, primary_key=True, autoincrement=True)
    sender_id = Column(Integer, ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    receiver_id = Column(Integer, ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    content = Column(Text, nullable=False)
    sent_at = Column(DateTime, default=datetime.utcnow)
    is_read = Column(Boolean, default=False)
    __table_args__ = (Index('idx_conversation', 'sender_id', 'receiver_id'),)
    sender = relationship('User', foreign_keys=[sender_id], back_populates='sent_messages')
    receiver = relationship('User', foreign_keys=[receiver_id], back_populates='received_messages')

class Match(Base):
    __tablename__ = 'matches'
    __table_args__ = (UniqueConstraint('teacher_id','student_id', name='unique_match'),)
    match_id = Column(Integer, primary_key=True, autoincrement=True)
    teacher_id = Column(Integer, ForeignKey('teachers.teacher_id', ondelete='CASCADE'), nullable=False)
    student_id = Column(Integer, ForeignKey('students.student_id', ondelete='CASCADE'), nullable=False)
    matched_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    teacher = relationship('Teacher', back_populates='matches')
    student = relationship('Student', back_populates='matches')

class Review(Base):
    __tablename__ = 'reviews'
    review_id = Column(Integer, primary_key=True, autoincrement=True)
    lesson_id = Column(Integer, ForeignKey('lessons.lesson_id', ondelete='SET NULL'))
    reviewer_id = Column(Integer, ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    reviewee_id = Column(Integer, ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    rating = Column(Integer, nullable=False)
    comment = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    lesson = relationship('Lesson', back_populates='reviews')
    reviewer = relationship('User', foreign_keys=[reviewer_id], back_populates='reviews_given')
    reviewee = relationship('User', foreign_keys=[reviewee_id], back_populates='reviews_received')

class MarketplaceProduct(Base):
    __tablename__ = 'marketplace_products'
    product_id = Column(Integer, primary_key=True, autoincrement=True)
    teacher_id = Column(Integer, ForeignKey('teachers.teacher_id', ondelete='CASCADE'), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    price = Column(DECIMAL(10,2), nullable=False)
    is_available = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    teacher = relationship('Teacher', back_populates='marketplace_products')
    orders = relationship('Order', back_populates='product', cascade='all, delete-orphan')

class Order(Base):
    __tablename__ = 'orders'
    order_id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey('students.student_id', ondelete='CASCADE'), nullable=False)
    product_id = Column(Integer, ForeignKey('marketplace_products.product_id', ondelete='SET NULL'))
    lesson_id = Column(Integer, ForeignKey('lessons.lesson_id', ondelete='SET NULL'))
    amount = Column(DECIMAL(10,2), nullable=False)
    status = Column(Enum('pending','completed','refunded', name='order_statuses'), default='pending')
    created_at = Column(DateTime, default=datetime.utcnow)
    student = relationship('Student', back_populates='orders')
    product = relationship('MarketplaceProduct', back_populates='orders')
    lesson = relationship('Lesson', back_populates='orders')

class AdminLog(Base):
    __tablename__ = 'admin_logs'
    log_id = Column(Integer, primary_key=True, autoincrement=True)
    admin_id = Column(Integer, ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    action = Column(String(50), nullable=False)
    details = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    admin = relationship('User', back_populates='admin_logs')

# --- XAMPP MySQL Connection & Initialization ---

DB_USER = 'root'
DB_PASSWORD = ''  # set your MySQL root password if any
DB_HOST = '127.0.0.1'
DB_PORT = 3306
DB_NAME = 'skillexx'

DATABASE_URL = f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Create engine & session factory
engine = create_engine(DATABASE_URL, echo=True, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

def init_db():
    """Connects to the database and creates all tables"""
    try:
        # Test connection
        with engine.connect() as conn:
            pass
        # Create tables
        Base.metadata.create_all(bind=engine)
        print(f"✅ Connected to XAMPP MySQL and created tables in '{DB_NAME}'")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")

if __name__ == "__main__":
    init_db()
