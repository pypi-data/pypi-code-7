# coding=utf-8
from __future__ import unicode_literals, print_function
from flask import request, current_app
from flask.ext.login import UserMixin, AnonymousUserMixin
from sqlalchemy.ext.hybrid import hybrid_property
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from datetime import datetime
import hashlib
from web_site import db, login_manager


class Permission:
    """使用32位整数表示权限"""
    # 评论
    USER = 0xff
    # 职员
    STAFF = 0xffff
    # 管理员
    ADMINISTRATOR = 0xffffffff


class RolePermission():
    """ role's permission """
    def __init__(self, name, permissions):
        self.name = name
        self.permissions = permissions

    @property
    def role(self):
        return Role.query.filter_by(name=self.name).first()


class SystemRoles:
    USER = RolePermission('User', Permission.USER)
    STAFF = RolePermission('Staff', Permission.STAFF)
    ADMINISTRATOR = RolePermission('Administrator', Permission.ADMINISTRATOR)

    roles = [USER, STAFF, ADMINISTRATOR]

    default = USER

    @staticmethod
    def is_default(r):
        return r == SystemRoles.default


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    desc = db.Column(db.Unicode(128), nullable=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.BigInteger, default=0x0)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return '<Role %r>' % self.name

    @staticmethod
    def insert_roles():
        for r in SystemRoles.roles:
            role = Role.query.filter_by(name=r.name).first()
            if role is None:
                role = Role(name=r.name)
            role.permissions = r.permissions
            role.default = SystemRoles.is_default(r)
            db.session.add(role)
        db.session.commit()


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    _email = db.Column('email', db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    password_hash = db.Column(db.String(128))
    user_permissions = db.Column(db.BigInteger, default=0x0)
    confirmed = db.Column(db.Boolean, default=False)

    # gravatar email hash
    _avatar_hash = db.Column('avatar_hash', db.String(32))

    # user info
    name = db.Column(db.String(64))
    location = db.Column(db.String(64))
    about_me = db.Column(db.Text())
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)

    def __init__(self, **kargs):
        super(User, self).__init__(**kargs)
        if self.role is None:
            if self.email in current_app.config['SYSTEM_ADMINS']:
                self.role = Role.query.filter_by(name='Administrator').first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()

    @hybrid_property
    def avatar_hash(self):
        if not self._avatar_hash:
            self.email = self._email
            db.session.add(self)
        return self._avatar_hash

    @hybrid_property
    def email(self):
        return self._email

    @email.setter
    def email(self, email):
        self._email = email
        self._avatar_hash = hashlib.md5(self.email.encode('utf-8')).hexdigest()

    @property
    def password(self):
        """密码不可读"""
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        """只保存密码的hash值"""
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        """校验密码"""
        return check_password_hash(self.password_hash, password)

    @property
    def permissions(self):
        """用户权限=角色权限+自身权限"""
        return (self.user_permissions | self.role.permissions) \
            if (self.role is not None and self.user_permissions is not None) \
            else self.role.permissions or self.user_permissions or 0x0

    def is_role(self, sr):
        """sr: SystemRoles.XXX"""
        return self.role is not None and self.role.name == sr.name

    def can(self, permissions):
        return (self.permissions & permissions) == permissions

    def is_administrator(self):
        return self.is_role(SystemRoles.ADMINISTRATOR)

    def generate_confirmation_token(self, expiration=3600):
        """生成确认token"""
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id})

    def reset_password(self, token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('reset') != self.id:
            return False
        self.password = new_password
        db.session.add(self)
        return True

    def generate_email_change_token(self, new_email, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'change_email': self.id, 'new_email': new_email})

    def change_email(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('change_email') != self.id:
            return False
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if self.query.filter_by(email=new_email).first() is not None:
            return False
        self.email = new_email
        db.session.add(self)
        return True

    def __repr__(self):
        return '<User %r>' % self.username

    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)

    def gravatar(self, size=100, default='identicon', rating='g'):
        if request.is_secure:
            url = 'https://secure.gravatar.com/avatar'
        else:
            url = 'http://www.gravatar.com/avatar'
        _hash = self.avatar_hash
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
            url=url, hash=_hash, size=size, default=default, rating=rating)


class AnonymousUser(AnonymousUserMixin):
    def is_role(self ,sr):
        return False

    def can(self, permissions):
        return False

    def is_administrator(self):
        return False


login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
