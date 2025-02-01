from flask import Flask, Response, request, render_template, current_app, Blueprint, jsonify, redirect, url_for, make_response
import hashlib
from datetime import datetime, timedelta
import jwt
import io

dashboard_ = Blueprint('dashboard', __name__)

@dashboard_.route('/dashboard')
def login_admin():
    myToken = request.cookies.get("mytoken")
    SECRET_KEY = current_app.config['SECRET_KEY']
    try:
        payload = jwt.decode(myToken, SECRET_KEY, algorithms=["HS256"])
        user_info = current_app.db.users.find_one({"username": payload["id"]})
        return render_template('dashboard_admin/dashboard.html', user_info=user_info)
    except jwt.ExpiredSignatureError:
        return redirect(url_for("auth_admin.login_admin"))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("auth_admin.login_admin"))
    

@dashboard_.route('/get-data', methods=['GET'])
def get_data():
    data_screening = list(current_app.db.status_screening.find({}, {'_id' : False}))
    data_materi = list(current_app.db.status.find({}, {'_id' : False}))
    return jsonify({"data_screening":data_screening, "data_materi": data_materi})

@dashboard_.route('/delete-screening', methods=['POST'])
def delete_screening():
    username = request.form['username']
    current_app.db.status_screening.delete_one({'username': username})
    return jsonify({'msg': 'Data screening berhasil dihapus!'})

@dashboard_.route('/delete-materi', methods=['POST'])
def delete_materi():
    username = request.form['username']
    materi = request.form['materi']
    current_app.db.status.delete_one({'username': username, 'materi': materi})
    return jsonify({'msg': 'Data materi berhasil dihapus!'})
