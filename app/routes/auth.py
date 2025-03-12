from flask import Flask, request, render_template, current_app, Blueprint, jsonify, redirect, url_for, make_response
import hashlib
from datetime import datetime, timedelta
import jwt
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer
import random
import string

auth_ = Blueprint('auth', __name__)
mail = Mail()

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
    email = request.form['email']
    password = request.form['password']
    password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()

    doc = {
        "namaLengkap": namaLengkap,
        "username": username,
        "email": email,
        "password": password_hash,
        "testimoni": "none",
        "profile": "",
        "profilePict": "assets/img/profile/profile.jpeg"
    }

    exists = bool(current_app.db.users.find_one({"$or": [
        {"username": username},
        {"email": email}
    ]}))
    
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

@auth_.route('/ubah-password')
def forget_password():
    return render_template('auth/ubah_password.html')

@auth_.route('/ubah-password-check', methods=["POST"])
def forget_password_check():
    username = request.form['username']
    password = request.form['password']
    pw_hash = hashlib.sha256(password.encode("utf-8")).hexdigest()
    newPassword = request.form["newPassword"]
    password_hash = hashlib.sha256(newPassword.encode('utf-8')).hexdigest()

    exists = current_app.db.users.find_one({
        "username": username,
        "password": pw_hash
    })
    if exists:
        current_app.db.users.update_one(
            {"username": username},
            {"$set": {"password": password_hash}}
        )
        return jsonify({'result': 'success', 'msg': 'Password successfully changed!'})

    return jsonify({'result': 'failed', 'msg': 'Email or password does not match!'})

@auth_.route('/forgot_password', methods=['POST'])
def forgot_password():
    try:
        username = request.form.get('username')
        email = request.form.get('email')
        print(f"Received request for username: {username}, email: {email}")  # Debug log
        
        if not username or not email:
            return jsonify({'result': 'error', 'msg': 'Username dan email harus diisi'})
            
        user = current_app.db.users.find_one({
            'username': username,
            'email': email
        })
        
        if not user:
            return jsonify({'result': 'error', 'msg': 'Username atau email tidak sesuai'})
        
        # Generate token
        serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        token = serializer.dumps(email, salt='reset-password')
        
        # Generate reset link
        reset_url = url_for('auth.reset_password_page', token=token, _external=True)
        print(f"Generated reset URL: {reset_url}")  # Debug log
        
        # Send email
        try:
            msg = Message(
                'Reset Password Request - PSI Damai',
                sender=('PSI Damai', current_app.config['MAIL_DEFAULT_SENDER']),
                recipients=[email]
            )
            
            msg.body = f'''
Yth. {user.get('namaLengkap', 'Pengguna PSI Damai')},

Anda telah meminta untuk mereset password untuk akun:
Username: {username}

Untuk melanjutkan proses reset password, silakan klik link berikut:
{reset_url}

Link ini akan kadaluarsa dalam 1 jam.

Jika Anda tidak meminta reset password, abaikan email ini.

Terima kasih,
Tim PSI Damai
'''
            mail.send(msg)
            print("Email sent successfully")  # Debug log
            return jsonify({'result': 'success', 'msg': 'Email reset password telah dikirim'})
            
        except Exception as e:
            print(f"Error sending email: {str(e)}")  # Debug log
            return jsonify({
                'result': 'error', 
                'msg': 'Gagal mengirim email. Silakan coba lagi atau hubungi administrator.'
            })
            
    except Exception as e:
        print(f"General error in forgot_password: {str(e)}")  # Debug log
        return jsonify({
            'result': 'error',
            'msg': 'Terjadi kesalahan sistem. Silakan coba lagi nanti.'
        })

@auth_.route('/reset_password/<token>', methods=['GET'])
def reset_password_page(token):
    try:
        serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        # Cek validitas token
        email = serializer.loads(token, salt='reset-password', max_age=3600)  # Token berlaku 1 jam
        
        # Jika token valid, tampilkan halaman reset password dengan token
        return render_template('auth/reset_password.html', token=token)
        
    except Exception as e:
        # Jika token tidak valid atau kadaluarsa, arahkan ke halaman login dengan pesan error
        return render_template('auth/login.html', 
                             reset_error="Link reset password tidak valid atau sudah kadaluarsa. "
                             "Silakan meminta link reset password baru.")

@auth_.route('/reset_password', methods=['POST'])
def reset_password():
    token = request.form.get('token')
    new_password = request.form.get('new_password')
    
    try:
        serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        email = serializer.loads(token, salt='reset-password', max_age=3600)
        password_hash = hashlib.sha256(new_password.encode('utf-8')).hexdigest()
        
        current_app.db.users.update_one(
            {'email': email},
            {'$set': {'password': password_hash}}
        )
        
        return jsonify({'result': 'success', 'msg': 'Password berhasil diubah'})
    except:
        return jsonify({'result': 'error', 'msg': 'Link reset password tidak valid atau sudah kadaluarsa'})