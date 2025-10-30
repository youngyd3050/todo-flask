from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_restful import Api

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
api = Api()

def create_app(config=None):
    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.config.from_mapping(
        SECRET_KEY='replace-me-in-prod',
        SQLALCHEMY_DATABASE_URI='sqlite:///' + str(app.instance_path) + '/todo.db',
        SQLALCHEMY_TRACK_MODIFICATIONS=False
    )
    if config:
        app.config.update(config)

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    api.init_app(app)          # ← 只留这一行，不要上面再写 api = Api(app)

    login_manager.login_view = 'main.login'   # 蓝图名.函数名
    login_manager.login_message = '请先登录'

    from . import models, views, api as api_module
    app.register_blueprint(views.bp)
    # 下面这一行删掉或注释掉
    # app.register_blueprint(api_module.bp)

    return app