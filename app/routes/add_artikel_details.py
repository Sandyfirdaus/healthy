from flask import Flask, request, render_template, current_app, Blueprint, jsonify, redirect, url_for
from werkzeug.utils import secure_filename
import jwt
import os

add_artikel_details_ = Blueprint('add_artikel_details', __name__)

@add_artikel_details_.route('/view-artikel-details')
def view_artikel_details():
    myToken = request.cookies.get("mytoken")
    SECRET_KEY = current_app.config['SECRET_KEY']
    try:
        payload = jwt.decode(myToken, SECRET_KEY, algorithms=["HS256"])
        
        user_info = current_app.db.users_admin.find_one({"username": payload["id"]})
        title = request.args.get('title')

        if not title:
            return redirect(url_for("add_artikel.view_artikel"))

        if user_info and user_info.get('username') == 'admin.psidamai':
            return render_template('dashboard_admin/artikel_details.html', user_info=user_info)
        else:
            return redirect(url_for("auth_admin.login_admin"))
        
    except jwt.ExpiredSignatureError:
        return redirect(url_for("auth_admin.login_admin"))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("auth_admin.login_admin"))
    

@add_artikel_details_.route('/detail-artikel/<title>')
def detail_artikel(title):
    article = current_app.db.artikel.find_one({'title': title}, {'_id' : False})
    return jsonify({'msg': 'Artikel berhasil ditemukan!', 'article': article})