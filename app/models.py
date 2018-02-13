#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import current_app
from itsdangerous import (
    TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired)
from passlib.apps import custom_app_context as pwd_context

from app import db


class Permission:
    COMMENT = 0x02
    WRITE_ARTICLES = 0x04
    MODERATE_COMMENTS = 0x08
    ADMIN = 0x80


class UserRole(db.Model):
    __tablename__ = 'role'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    user = db.relationship('User', backref='UserRole', lazy='dynamic', cascade='all, delete-orphan')

    @staticmethod
    def insert_roles():
        roles = {
            'user': (Permission.COMMENT |
                     Permission.WRITE_ARTICLES, True),
            'admin': (0xff, False)
        }
        for r in roles:
            role = UserRole.query.filter_by(name=r).first()
            if role is None:
                role = UserRole(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return '<UserRole(nanme={}, permissions={})>'.format(self.name, self.permissions)


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Unicode(32, collation='utf8_bin'), nullable=False, unique=True, index=True)
    password_hash = db.Column(db.Unicode(256, collation='utf8_bin'), nullable=False)
    email = db.Column(db.Unicode(20, collation='utf8_bin'))
    role = db.relationship('UserRole', backref='User', uselist=False, lazy='select')

    def __repr__(self):
        return '<User(username={})>'.format(self.username)

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role_id is None:
            if self.username == 'admin':
                role = UserRole.query.filter_by(permissions=0xff).first()
            else:
                role = UserRole.query.filter_by(default=True).first()
            self.role_id = role.id

    def operation(self, permissions):
        return self.role_id is not None and (self.role.permissions & permissions) == permissions

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = pwd_context.hash(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

    def generate_auth_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({'id': self.id})

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None  # valid token, but expired
        except BadSignature:
            return None  # invalid token
        user = User.query.get(data['id'])
        return user

    def to_json(self):
        json = {
            'id': self.id,
            'username': self.username,
            'email': self.email
        }
        return json


class AnonymousUser(User):
    def operation(self, permissions):
        return False
