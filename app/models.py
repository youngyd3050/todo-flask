from datetime import datetime
from flask_login import UserMixin
from . import db, login_manager

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    id       = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True, nullable=False)
    email    = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    tasks    = db.relationship('Task', backref='owner', lazy=True, cascade='all, delete-orphan')

# class Task(db.Model):
#     id        = db.Column(db.Integer, primary_key=True)
#     title     = db.Column(db.String(200), nullable=False)
#     done      = db.Column(db.Boolean, default=False)
#     user_id   = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
#     priority  = db.Column(db.Integer, default=1)   # ★ 1=高 2=中 3=低
#


class Task(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    title       = db.Column(db.String(200), nullable=False)
    done        = db.Column(db.Boolean, default=False)
    user_id     = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    priority    = db.Column(db.Integer, default=2)          # 1高 2中 3低
    description = db.Column(db.Text)                        # ★ 任务介绍
    start_time  = db.Column(db.DateTime, default=datetime.utcnow)  # ★ 开始
    end_time    = db.Column(db.DateTime)                    # ★ 结束
    # 1=待办 2=进行中 3=已完成
    status = db.Column(db.Integer, default=1, nullable=True)   # 先允许空