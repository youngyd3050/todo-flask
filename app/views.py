from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from . import db
from .models import Task, User
from .forms import RegistrationForm, LoginForm

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