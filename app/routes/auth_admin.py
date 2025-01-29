from flask import Flask, request, render_template, current_app, Blueprint, jsonify, redirect, url_for, make_response
import hashlib
from datetime import datetime, timedelta
import jwt

auth_admin_ = Blueprint('auth_admin', __name__)

@auth_admin_ .route('/login-admin')
def login_admin():
    return render_template('auth_admin/login.html')

@auth_admin_ .route('/login-admin/check', methods=["POST"])
def login_admin_check():
    username = request.form["username"]
    password = request.form["password"]
    pw_hash = hashlib.sha256(password.encode("utf-8")).hexdigest()
    SECRET_KEY = current_app.config['SECRET_KEY']

    user_info = current_app.db.users_admin.find_one({
        "username": username,
        "password": pw_hash
    })

    if user_info:
        payload = {
            "id": username,
            "exp": datetime.utcnow() + timedelta(hours=3)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
        return jsonify({
            "result": "success",
            "token": token
        })
    else:
        return jsonify({
            "result": "fail",
            "msg": "Username atau Password Salah!"
        })

@auth_admin_ .route('/register-admin')
def register_admin():
    return render_template('auth_admin/register.html')

@auth_admin_ .route('/register-admin/save', methods=["POST"])
def register_admin_save():
    namaLengkap = request.form['name']
    username = request.form['email']
    password = request.form['password']
    password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()

    doc = {
        "namaLengkap": namaLengkap,
        "username": username,
        "password": password_hash,
        "profilePict": "assets/img/profile/profile.jpeg"
    }

    current_app.db.users_admin.insert_one(doc)

    return jsonify({'msg': "Successfully created"})

