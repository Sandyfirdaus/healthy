from flask import Flask, request, render_template, current_app, Blueprint, jsonify, redirect, url_for
from werkzeug.utils import secure_filename
import jwt
import os

add_program_ = Blueprint('add_program', __name__)

@add_program_.route('/view-program')
def view_program():
    myToken = request.cookies.get("mytoken")
    SECRET_KEY = current_app.config['SECRET_KEY']
    try:
        payload = jwt.decode(myToken, SECRET_KEY, algorithms=["HS256"])
        
        user_info = current_app.db.users_admin.find_one({"username": payload["id"]})

        if user_info and user_info.get('username') == 'admin.psidamai':
            return render_template('dashboard_admin/program.html', user_info=user_info)
        else:
            return redirect(url_for("auth_admin.login_admin"))
        
    except jwt.ExpiredSignatureError:
        return redirect(url_for("auth_admin.login_admin"))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("auth_admin.login_admin"))

@add_program_.route('/get-program', methods=['GET'])
def get_program():
    data_program = list(current_app.db.program.find({}, {'_id': False}))
    return jsonify({"data_program": data_program})

@add_program_.route('/add-program', methods=['POST'])
def add_program():
    title = request.form['title']
    newDoc = {'title': title}

    if "fileCover" in request.files:
        file = request.files["fileCover"]
        if file.filename != '':
            filename = secure_filename(file.filename)
            extension = filename.split(".")[-1]
            file_path = f"assets/img/program/{title}.{extension}"

            upload_dir = os.path.join(current_app.root_path, "static", "assets", "img", "program")
            if not os.path.exists(upload_dir):
                os.makedirs(upload_dir)

            file.save(os.path.join(upload_dir, f"{title}.{extension}"))
            newDoc["coverImage"] = file_path

    current_app.db.program.insert_one(newDoc)
    return jsonify({'msg': 'Program berhasil ditambahkan!'})

@add_program_.route('/delete-program', methods=['POST'])
def delete_programi():
    title = request.form['title']
    current_app.db.program.delete_one({'title': title})
    return jsonify({'msg': 'Data program berhasil dihapus!'})

@add_program_.route('/edit-program', methods=['POST'])
def edit_program():
    title = request.form['title']
    new_title = request.form['new_title']
    update_fields = {
        'title': new_title,
    }
    
    # Update gambar program jika ada
    if 'filePict' in request.files:
        file = request.files['filePict']
        if file.filename:
            filename = secure_filename(file.filename)
            extension = filename.split('.')[-1]
            file_path = f"assets/img/program/{new_title}.{extension}"
            upload_dir = os.path.join(current_app.root_path, "static", "assets", "img", "program")
            if not os.path.exists(upload_dir):
                os.makedirs(upload_dir)
            file.save(os.path.join(upload_dir, f"{new_title}.{extension}"))
            update_fields['coverImage'] = file_path  # Ubah dari programPict ke coverImage
    
    # Update data di database
    result = current_app.db.program.update_one({'title': title}, {'$set': update_fields})
    
    if result.modified_count:
        return jsonify({'msg': 'Program berhasil diperbarui!', 'updated_fields': update_fields})
    else:
        return jsonify({'msg': 'Tidak ada perubahan atau program tidak ditemukan.'}), 400


@add_program_.route('/detail-program/<title>')
def detail_program(title):
    program = current_app.db.program.find_one({'title': title}, {'_id' : False})
    return jsonify({'msg': 'program berhasil ditemukan!', 'program': program})
