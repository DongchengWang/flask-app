# . 引用app/__init__.py
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_required

# from flask_login import login_required
from . import login_manager
from . import db


@login_manager.user_loader
def load_user(user_id):
    """使用指定的id来加载用户"""
    return User.query.get(int(user_id))


# @app.route('/secret')
# @login_required
# def secret():
#     '''保护路由只让认证用户访问'''
#     return 'Only authenticated users are allowed!'


class Role(db.Model):
    """数据库操作"""

    __tablename__ = "roles"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship("User", backref="role", lazy="dynamic")

    def __repr__(self):
        return "<Role %r>" % self.name


class User(UserMixin, db.Model):
    """用户模型"""

    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    role_id = db.Column(db.Integer, db.ForeignKey("roles.id"))

    @property
    def password(self):
        raise AttributeError("password is not  a  readable attribute")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return "<User %r>" % self.username
