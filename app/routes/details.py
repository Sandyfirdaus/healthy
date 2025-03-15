from flask import Flask, request, render_template, current_app, Blueprint, jsonify, redirect, url_for
from werkzeug.utils import secure_filename
import jwt

details_ = Blueprint('details', __name__)

@details_.route('/details')
def details():
    myToken = request.cookies.get("mytoken")
    if not myToken:
        return redirect(url_for("auth_admin.login_admin"))

    SECRET_KEY = current_app.config.get('SECRET_KEY')
    if not SECRET_KEY:
        return redirect(url_for("auth_admin.login_admin"))

    try:
        payload = jwt.decode(myToken, SECRET_KEY, algorithms=["HS256"])
        user_info = current_app.db.users_admin.find_one({"username": payload.get("id")})

        if user_info and user_info.get('username') == 'admin.psidamai':
            return render_template('dashboard_admin/details.html', user_info=user_info)

    except (jwt.ExpiredSignatureError, jwt.DecodeError):
        return redirect(url_for("auth_admin.login_admin"))

    return redirect(url_for("auth_admin.login_admin"))

@details_.route('/get-materi', methods=['GET'])
def get_materi():
    data_materi = list(current_app.db.status_materi.find({}, {'_id': False}))
    return jsonify({"data_materi": data_materi})

@details_.route('/delete-materi', methods=['POST'])
def delete_materi():
    username = request.form.get('username')
    materi = request.form.get('materi')

    if not username or not materi:
        return jsonify({'msg': 'Data tidak lengkap!'}), 400

    result = current_app.db.status_materi.delete_one({'username': username, 'materi': materi})

    if result.deleted_count == 0:
        return jsonify({'msg': 'Data materi tidak ditemukan!'}), 404

    return jsonify({'msg': 'Data materi berhasil dihapus!'})
