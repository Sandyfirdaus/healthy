from flask import Flask, request, render_template, current_app, Blueprint, jsonify, redirect, url_for, make_response
import hashlib
from datetime import datetime, timedelta
import jwt

dashboard_ = Blueprint('dashboard', __name__)

@dashboard_.route('/dashboard')
def login_admin():
    return render_template('dashboard_admin/dashboard.html')

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