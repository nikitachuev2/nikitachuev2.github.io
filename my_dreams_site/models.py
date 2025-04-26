
from app import db
from flask_login import UserMixin

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    purchases = db.relationship('Purchase', backref='owner', lazy=True)
    goals = db.relationship('Goal', backref='goal_owner', lazy=True)
    contributions = db.relationship('Contribution', backref='contributor', lazy=True)

class Purchase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())  # Для анализа по времени

class Goal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    target_amount = db.Column(db.Float, nullable=False)
    current_amount = db.Column(db.Float, default=0)
    dream_name = db.Column(db.String(100), nullable=False)  # Поле для названия мечты

class Contribution(db.Model):  # Модель для учета внесенных средств
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())

# Список популярных категорий для расходов
POPULAR_CATEGORIES = [
    'Еда',
    'Транспорт',
    'Развлечения',
    'Одежда',
    'Квартира',
    'Коммунальные услуги',
    'Образование',
    'Путешествия',
    'Здоровье',
    'Спорт'
]
