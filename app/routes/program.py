from flask import Flask, request, render_template, current_app, Blueprint, jsonify, redirect, url_for
import jwt
from datetime import datetime

program_ = Blueprint('program', __name__)

@program_.route('/program')
def program():
    myToken = request.cookies.get("mytoken")
    SECRET_KEY = current_app.config['SECRET_KEY']
    try:
        payload = jwt.decode(myToken, SECRET_KEY, algorithms=["HS256"])
        user_info = current_app.db.users.find_one({"username": payload["id"]})
        return render_template('dashboard/program.html', user_info=user_info)
    except jwt.ExpiredSignatureError:
        return redirect(url_for("auth.login"))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("auth.login"))

@program_.route('/save-status-screening', methods=["POST"])
def save_status_screening():
    try:
        username = request.form['username']
        scoreScreening = request.form['resultText']
        tanggal = request.form['tanggal']
        jam = request.form['jam']
        
        # Dapatkan email user dari database users
        user = current_app.db.users.find_one({"username": username})
        email = user.get('email') if user else None
        
        # Buat dokumen baru untuk setiap screening
        doc = {
            "username": username,
            "email": email,
            "scoreScreening": scoreScreening,
            "tanggal": tanggal,
            "jam": jam,
            "timestamp": datetime.now()  # Tambahkan timestamp untuk pengurutan
        }

        # Selalu insert dokumen baru
        current_app.db.status_screening.insert_one(doc)
        
        return jsonify({
            "result": "Success",
            "tanggal": tanggal,
            "jam": jam
        })
    except Exception as e:
        print("Error saving screening:", str(e))
        return jsonify({
            "result": "Error",
            "message": "Gagal menyimpan data screening"
        }), 500

@program_.route('/check-status-screening', methods=["POST"])
def check_status_screening():
    username = request.form['username']

    exists = bool(current_app.db.status_screening.find_one({"username": username}))
    if exists:
        return jsonify({
            "exists": exists,
            "result": "Sudah Pernah Screening",
        })
    else:
        return jsonify({
            "exists": exists,
            "result": "Belum Pernah Screening",
        })
