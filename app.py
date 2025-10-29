# from flask import Flask
# app = Flask(__name__)
#
# @app.route('/')
# def index():
#     return 'Hello Flask!'


# from flask import Flask
#
# app = Flask(__name__)
#
# @app.route('/')
# def hello():
#     return 'Hello Flask!'
#
# if __name__ == '__main__':
#     app.run()


from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__,
            template_folder='app/templates',
            static_folder='app/static')
# 把 sqlite 文件放到 instance 文件夹，git 可忽略
instance_path = os.path.join(os.path.dirname(__file__), 'instance')
os.makedirs(instance_path, exist_ok=True)
db_path = os.path.join(instance_path, 'todo.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ----- 模型 -----
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    done = db.Column(db.Boolean, default=False)

# ----- 首次运行时创建表 -----
with app.app_context():
    db.create_all()

# ----- 路由 -----
@app.route('/')
def index():
    tasks = Task.query.all()
    return render_template('index.html', tasks=tasks)

@app.route('/add', methods=['POST'])
def add():
    title = request.form.get('title', '').strip()
    if title:
        db.session.add(Task(title=title))
        db.session.commit()
    return redirect(url_for('index'))

@app.route('/toggle/<int:task_id>', methods=['POST'])
def toggle(task_id):
    task = Task.query.get_or_404(task_id)
    task.done = not task.done
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/delete/<int:task_id>', methods=['POST'])
def delete(task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for('index'))









if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)