from flask import Flask, request, render_template, current_app, Blueprint, jsonify, redirect, url_for
from werkzeug.utils import secure_filename
import jwt

screening_ = Blueprint('screening', __name__)

@screening_.route('/screening')
def screening():
    myToken = request.cookies.get("mytoken")
    SECRET_KEY = current_app.config['SECRET_KEY']
    try:
        payload = jwt.decode(myToken, SECRET_KEY, algorithms=["HS256"])
        
        user_info = current_app.db.users_admin.find_one({"username": payload["id"]})

        if user_info and user_info.get('username') == 'admin.psidamai':
            return render_template('dashboard_admin/screening.html', user_info=user_info)
        else:
            return redirect(url_for("auth_admin.login_admin"))
        
    except jwt.ExpiredSignatureError:
        return redirect(url_for("auth_admin.login_admin"))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("auth_admin.login_admin"))

@screening_.route('/get-screening', methods=['GET'])
def get_screening():
    # Ambil semua data screening dan urutkan berdasarkan timestamp terbaru
    data_screening = list(current_app.db.status_screening.find(
        {}, 
        {'_id': False}
    ).sort([("timestamp", -1)])  # -1 untuk descending order
    )
    
    # Format data untuk ditampilkan
    for item in data_screening:
        if 'timestamp' in item:
            del item['timestamp']  # Hapus timestamp dari output JSON
            
    return jsonify({"data_screening": data_screening})

@screening_.route('/delete-screening', methods=['POST'])
def delete_screening():
    username = request.form['username']
    tanggal = request.form['tanggal']
    jam = request.form['jam']
    
    # Hapus data spesifik berdasarkan username, tanggal, dan jam
    current_app.db.status_screening.delete_one({
        'username': username,
        'tanggal': tanggal,
        'jam': jam
    })
    return jsonify({'msg': 'Data screening berhasil dihapus!'})
