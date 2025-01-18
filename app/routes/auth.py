from flask import Flask, request, render_template, current_app, Blueprint, jsonify, redirect, url_for, make_response
import hashlib
from datetime import datetime, timedelta
import jwt

auth_ = Blueprint('auth', __name__)

@auth_.route('/login')
def login():
    return render_template('auth/login.html')

@auth_.route('/login/check', methods=["POST"])
def login_check():
    username = request.form["username"]
    password = request.form["password"]
    pw_hash = hashlib.sha256(password.encode("utf-8")).hexdigest()
    SECRET_KEY = current_app.config['SECRET_KEY']

    user_info = current_app.db.users.find_one({
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

@auth_.route('/register')
def register():
    return render_template('auth/register.html')

@auth_.route('/register/save', methods=["POST"])
def register_save():
    namaLengkap = request.form['namaLengkap']
    username = request.form['username']
    password = request.form['password']
    password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()

    doc = {
        "namaLengkap": namaLengkap,
        "username": username,
        "password": password_hash,
        "testimoni": "none",
        "profile": "",
        "profilePict": "assets/img/profile/profile.jpeg"
    }

    exists = bool(current_app.db.users.find_one({"username": username}))
    if not exists:
        current_app.db.users.insert_one(doc)

    return jsonify({'exists': exists})

@auth_.route("/logout", methods=["DELETE"])
def logout():
    try:
        response = {"message": "Token successfully deleted"}
        resp = make_response(jsonify(response))
        resp.set_cookie("mytoken", "", expires=0, path="/")
        return resp
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        response = {"message": "Invalid token"}
        return jsonify(response), 401

@auth_.route('/forget-password')
def forget_password():
    return render_template('auth/forget-password.html')

@auth_.route('/forget-password-check', methods=["POST"])
def forget_password_check():
    username = request.form['username']
    password = request.form['password']
    password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()

    exists = bool(current_app.db.users.find_one({"username": username}))
    if exists:
        current_app.db.users.update_one(
            {"username": username},
            {"$set": {"password": password_hash}}
        )
        return jsonify({'result': 'success', 'msg': 'Password successfully changed!'})

    return jsonify({'result': 'failed', 'msg': 'Email does not match!'})
