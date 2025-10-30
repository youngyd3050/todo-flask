from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from . import db
from .models import Task, User
from .forms import RegistrationForm, LoginForm
from flask import jsonify, request
from datetime import datetime
from .forms import TaskForm
from .models import Task

bp = Blueprint('main', __name__)

from flask import request, render_template
from flask_login import login_required, current_user
from sqlalchemy import or_
from .forms import SearchForm
from .models import Task

PER_PAGE = 5

@bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    form = SearchForm()
    q = Task.query.filter_by(owner=current_user)

    # 搜索
    if form.validate_on_submit():
        kw = form.keyword.data.strip()
        pr = form.priority.data
        if kw:
            q = q.filter(Task.title.contains(kw))
        if pr:
            q = q.filter(Task.priority == int(pr))
        return redirect(url_for('main.index', keyword=kw, priority=pr or ''))

    # 读取查询参数（分页时保留条件）
    kw = request.args.get('keyword', '')
    pr = request.args.get('priority', '')
    if kw:
        q = q.filter(Task.title.contains(kw))
    if pr:
        q = q.filter(Task.priority == int(pr))

    # 排序：高优在前
    q = q.order_by(Task.priority, Task.id.desc())
    page = request.args.get('page', 1, type=int)
    pagination = q.paginate(page=page, per_page=PER_PAGE, error_out=False)

    return render_template('index.html',
                           form=form,
                           tasks=pagination.items,
                           pagination=pagination,
                           keyword=kw,
                           priority=pr)

# ---------------- 用户认证 ----------------
@bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        from werkzeug.security import generate_password_hash
        user = User(username=form.username.data,
                    email=form.email.data,
                    password=generate_password_hash(form.password.data))
        db.session.add(user)
        db.session.commit()
        flash('注册成功，请登录', 'success')
        return redirect(url_for('main.login'))
    else:
	    print('>>> register errors:', form.errors)  # ← 新增
    return render_template('register.html', form=form)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        from werkzeug.security import check_password_hash
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('main.index'))
        flash('用户名或密码错误', 'danger')
    return render_template('login.html', form=form)

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('已退出登录', 'info')
    return redirect(url_for('main.login'))

# ---------------- Todo 功能 ----------------
@bp.route('/add', methods=['POST'])
@login_required
def add():
    title = request.form.get('title', '').strip()
    priority = int(request.form.get('priority', 1))   # ★ 读优先级
    if title:
        db.session.add(Task(title=title, priority=priority, owner=current_user))
        db.session.commit()
    return redirect(url_for('main.index'))

@bp.route('/toggle/<int:task_id>', methods=['POST'])
@login_required
def toggle(task_id):
    task = Task.query.filter_by(id=task_id, owner=current_user).first_or_404()
    task.done = not task.done
    db.session.commit()
    return redirect(url_for('main.index'))

@bp.route('/delete/<int:task_id>', methods=['POST'])
@login_required
def delete(task_id):
    task = Task.query.filter_by(id=task_id, owner=current_user).first_or_404()
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for('main.index'))



# ⑤ 弹出框新增
@bp.route('/add_modal', methods=['POST'])
@login_required
def add_modal():
    form = TaskForm()
    if form.validate_on_submit():
        task = Task(
            title=form.title.data,
            priority=form.priority.data,
            description=form.description.data,
            start_time=form.start_time.data,
            end_time=form.end_time.data,
            owner=current_user
        )
        db.session.add(task)
        db.session.commit()
        return jsonify({'ok': True})
    return jsonify({'ok': False, 'errors': form.errors}), 400

# ⑥ 编辑回显
@bp.route('/edit/<int:task_id>')
@login_required
def edit_task(task_id):
    task = Task.query.filter_by(id=task_id, owner=current_user).first_or_404()
    return jsonify({
        'id': task.id,
        'title': task.title,
        'priority': task.priority,
        'description': task.description or '',
        'start_time': task.start_time.strftime('%Y-%m-%dT%H:%M') if task.start_time else '',
        'end_time': task.end_time.strftime('%Y-%m-%dT%H:%M') if task.end_time else ''
    })

# ⑦ 保存修改
@bp.route('/update/<int:task_id>', methods=['POST'])
@login_required
def update_task(task_id):
    task = Task.query.filter_by(id=task_id, owner=current_user).first_or_404()
    form = TaskForm()
    if form.validate_on_submit():
        task.title = form.title.data
        task.priority = form.priority.data
        task.description = form.description.data
        task.start_time = form.start_time.data
        task.end_time = form.end_time.data
        db.session.commit()
        return jsonify({'ok': True})
    return jsonify({'ok': False, 'errors': form.errors}), 400




# 看板页面
@bp.route('/kanban')
@login_required
def kanban():
    todo  = Task.query.filter_by(owner=current_user, status=1).all()
    doing = Task.query.filter_by(owner=current_user, status=2).all()
    done  = Task.query.filter_by(owner=current_user, status=3).all()
    return render_template('kanban.html', todo=todo, doing=doing, done=done)

# 拖拽换列
@bp.route('/move/<int:task_id>', methods=['POST'])
@login_required
def move_task(task_id):
    task = Task.query.filter_by(id=task_id, owner=current_user).first_or_404()
    new_status = request.json['status']
    if new_status in (1, 2, 3):
        task.status = new_status
        db.session.commit()
        return jsonify({'ok': True})
    return jsonify({'ok': False}), 400