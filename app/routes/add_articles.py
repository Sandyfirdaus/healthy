from flask import Flask, Response, request, render_template, current_app, Blueprint, jsonify, redirect, url_for, make_response
import hashlib
from datetime import datetime, timedelta
import jwt
import io

add_articles_ = Blueprint('add_articles', __name__)

@add_articles_.route('/dashboard')
def login_admin():
    myToken = request.cookies.get("mytoken")
    SECRET_KEY = current_app.config['SECRET_KEY']
    try:
        # Decode JWT token
        payload = jwt.decode(myToken, SECRET_KEY, algorithms=["HS256"])
        
        # Cari user info berdasarkan username yang ada di payload
        user_info = current_app.db.users_admin.find_one({"username": payload["id"]})

        # Cek jika user_info ada dan username-nya sesuai dengan 'admin.psidamai'
        if user_info and user_info.get('username') == 'admin.psidamai':
            return render_template('dashboard_admin/dashboard.html', user_info=user_info)
        else:
            # Jika username bukan admin.psidamai, redirect ke halaman login
            return redirect(url_for("auth_admin.login_admin"))
        
    except jwt.ExpiredSignatureError:
        # Token sudah expired, redirect ke halaman login
        return redirect(url_for("auth_admin.login_admin"))
    except jwt.exceptions.DecodeError:
        # Jika token tidak valid
        return redirect(url_for("auth_admin.login_admin"))
    
@add_articles_.route('/add_articles')
def add_articles():
    return render_template('dashboard_admin/add_articles.html')