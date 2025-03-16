from flask import Flask, request, render_template, current_app, Blueprint, jsonify, redirect, url_for
from werkzeug.utils import secure_filename
import jwt
import logging

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
    
    print(f"Attempting to delete - username: {username}, materi: {materi}")
    
    try:
        # Delete from status_materi collection
        current_app.db.status_materi.delete_many({
            'username': username,
            'materi': materi
        })
        
        # Delete from save_materi collection
        current_app.db.save_materi.delete_many({
            'username': username,
            'materi': materi
        })
        
        # Delete from status collection
        current_app.db.status.delete_many({
            'username': username,
            'materi': materi
        })
        
        # Delete from progres collection
        current_app.db.progres.delete_many({
            'username': username,
            'materi': materi
        })
        
        # Reset user progress
        program_info = current_app.db.materi.find_one({'title': materi})
        if program_info and 'program_title' in program_info:
            program_title = program_info['program_title']
            current_app.db.users.update_one(
                {'username': username},
                {'$set': {'current_progress.' + program_title: 0}}
            )
        
        print(f"Successfully deleted data for username: {username}, materi: {materi}")
        return jsonify({'msg': 'Data materi berhasil dihapus!'})
    
    except Exception as e:
        print(f"Error deleting data: {str(e)}")
        return jsonify({'msg': f'Error: {str(e)}'}), 500
