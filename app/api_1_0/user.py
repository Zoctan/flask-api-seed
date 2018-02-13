#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time
from flask import request, jsonify, g
from .authentication import verify_password, unauthorized, get_token
from ..models import User, UserRole, db, Permission
from . import api, decorator
from tools import Verify


@api.route('/users', methods=['GET'])
@decorator.permission_required(Permission.ADMIN)
def get_all_users():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    paginate = User.query.order_by(User.id.desc()).paginate(page, per_page=per_page, error_out=False)
    return jsonify({'msg': 'ok', 'result': [item.to_json() for item in paginate.items]})


@api.route('/users/<id>', methods=['GET'])
def get_user_info(id):
    user_info = User.query.filter_by(user_id=id).first()
    if not user_info:
        return jsonify({'msg': 'no', 'error': 'user doesn\'t exist'})
    return jsonify({'msg': 'ok', 'result': [user_info.to_json()]})


@api.route('/tokens', methods=['POST'])
@decorator.json_required
def login():
    username = request.json.get('username')
    password = request.json.get('password')
    duration = request.json.get('duration')
    if username and password and verify_password(username, password):
        g.current_user.info.login_time = time.strftime('%Y-%m-%d %H:%M:%S')
        return get_token(duration)
    return unauthorized('login error')


@api.route('/tokens', methods=['DELETE'])
def logout():
    return jsonify({'msg': 'ok'})


@api.route('/users', methods=['POST'])
@decorator.json_required
def create_user():
    email = request.json.get('email')
    username = request.json.get('username')
    password = request.json.get('password')
    duration = request.json.get('duration')
    # require these value
    if not username or not password or not email:
        return jsonify({'msg': 'no', 'error': 'missing arguments, require: email, username, password'})
    if not Verify.email(email):
        return jsonify({'msg': 'no', 'error': 'email format wrong'})
    # user or email is already existed
    if User.query.filter_by(username=username).first():
        return jsonify({'msg': 'no', 'error': 'username: {} is already existed'.format(username)})
    if User.query.filter_by(email=email).first():
        return jsonify({'msg': 'no', 'error': 'email: {} is already existed'.format(email)})
    g.current_user = User(email=email, username=username)
    g.current_user.password = password
    db.session.add(g.current_user)
    db.session.flush()
    return get_token(duration)


@api.route('/users', methods=['PUT'])
@decorator.json_required
def update_user():
    user_info = User.query.filter_by(user_id=g.current_user.id).first()
    # just only modify these attribution
    keyword = {'realname', 'school', 'about_me', 'tag'}
    if not set(request.json.keys()).issubset(keyword):
        return jsonify({'msg': 'no', 'error': 'can not modify'})
    for key in request.json:
        # set user's old attribution as json value
        setattr(user_info, key, request.json.get(key))
    return jsonify({'msg': 'ok'})


@api.route('/users/password', methods=['PUT'])
@decorator.json_required
def update_user_password():
    old = User.query.get(g.current_user.id)
    if not set(request.json.keys()) == {'oldpassword', 'newpassword'}:
        return jsonify({'msg': 'no', 'error': 'can not modify'})
    # check old password that is correct or not
    # after modify, must logout!
    if not verify_password(old.username, request.json.get('oldpassword')):
        return jsonify({'msg': 'no', 'error': 'old password not correct'})
    old.password = request.json.get('newpassword')
    return jsonify({'msg': 'ok'})


@api.route('/users/<id>/role', methods=['PUT'])
@decorator.json_required
@decorator.permission_required(Permission.ADMIN)
def update_user_role(id):
    user = User.query.get(id)
    role = UserRole.query.filter_by(name=request.json.get('role')).first()
    user.role_id = role.id
    return jsonify({'msg': 'ok'})


@api.route('/users/<id>', methods=['DELETE'])
@decorator.permission_required(Permission.ADMIN)
def delete_user(id):
    user = User.query.get(id)
    if not user:
        return jsonify({'msg': 'no', 'error': 'user doesn\'t exist'})
    db.session.delete(user)
    return jsonify({'msg': 'ok'})
