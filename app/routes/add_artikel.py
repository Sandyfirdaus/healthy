from flask import Flask, request, render_template, current_app, Blueprint, jsonify, redirect, url_for
from werkzeug.utils import secure_filename
import jwt
import os
from bson import json_util, ObjectId
import re

add_artikel_ = Blueprint('add_artikel', __name__)

def sanitize_filename(title):
    """
    Sanitizes a title for use in filenames while preserving the original title for display.
    Replaces special characters with underscores.
    """
    return re.sub(r'[^\w\s-]', '_', title).strip()

@add_artikel_.route('/view-artikel')
def screening():
    myToken = request.cookies.get("mytoken")
    SECRET_KEY = current_app.config['SECRET_KEY']
    try:
        payload = jwt.decode(myToken, SECRET_KEY, algorithms=["HS256"])
        
        user_info = current_app.db.users_admin.find_one({"username": payload["id"]})

        if user_info and user_info.get('username') == 'admin.psidamai':
            return render_template('dashboard_admin/artikel.html', user_info=user_info)
        else:
            return redirect(url_for("auth_admin.login_admin"))
        
    except jwt.ExpiredSignatureError:
        return redirect(url_for("auth_admin.login_admin"))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("auth_admin.login_admin"))

@add_artikel_.route('/get-artikel', methods=['GET'])
def get_artikel():
    data_artikel = list(current_app.db.artikel.find({}, {'_id' : False}))
    return jsonify({"data_artikel":data_artikel})

@add_artikel_.route('/add-artikel', methods=['POST'])
def add_artikel():
    title = request.form['title']
    kategori = request.form['kategori']
    author = request.form['author']
    date = request.form['date'] 
    konten = request.form['konten']
    
    # Create sanitized filename for file storage
    safe_filename = sanitize_filename(title)
    
    newDoc = {
        'title': title,  # Store original title with special characters
        'kategori': kategori,
        'author': author,
        'date': date,
        'konten': konten,
    }
    
    if "filePict" in request.files:
        file = request.files["filePict"]
        if file.filename != '':  
            filename = secure_filename(file.filename)
            extension = filename.split(".")[-1]
            file_path = f"assets/img/artikel/{safe_filename}.{extension}"

            upload_dir = os.path.join(current_app.root_path, "static", "assets", "img", "artikel")
            if not os.path.exists(upload_dir):
                os.makedirs(upload_dir)

            file.save(os.path.join(upload_dir, f"{safe_filename}.{extension}"))

            newDoc["artikel"] = filename
            newDoc["artikelPict"] = file_path
    
    if "fileAuthor" in request.files:
        fileAuthor = request.files["fileAuthor"]
        if fileAuthor.filename != '':  
            filename = secure_filename(fileAuthor.filename)
            extensionAuthor = filename.split(".")[-1]
            file_path_author = f"assets/img/authors/{safe_filename}.{extensionAuthor}"
            upload_dir_author = os.path.join(current_app.root_path, "static", "assets", "img", "authors")
            if not os.path.exists(upload_dir_author):
                os.makedirs(upload_dir_author)
            fileAuthor.save(os.path.join(upload_dir_author, f"{safe_filename}.{extensionAuthor}"))
            newDoc["authorPict"] = file_path_author
    
    current_app.db.artikel.insert_one(newDoc)
    return jsonify({'msg': 'Add artikel sukses!'})
    
@add_artikel_.route('/delete-artikel', methods=['POST'])
def delete_artikel():
    title = request.form['title']
    current_app.db.artikel.delete_one({'title': title})
    return jsonify({'msg': 'Data artikel berhasil dihapus!'})

@add_artikel_.route('/edit-artikel', methods=['POST'])
def edit_artikel():
    title = request.form['title']
    new_title = request.form['new_title']
    kategori = request.form['kategori']
    author = request.form['author']
    date = request.form['date']
    konten = request.form['konten']
    
    # Create sanitized filename for file storage
    safe_new_title = sanitize_filename(new_title)
    
    update_fields = {
        'title': new_title,  # Store original title with special characters
        'kategori': kategori,
        'author': author,
        'date': date,
        'konten': konten,
    }
    
    # Update gambar artikel jika ada
    if 'filePict' in request.files:
        file = request.files['filePict']
        if file.filename:
            filename = secure_filename(file.filename)
            extension = filename.split('.')[-1]
            file_path = f"assets/img/artikel/{safe_new_title}.{extension}"
            upload_dir = os.path.join(current_app.root_path, "static", "assets", "img", "artikel")
            if not os.path.exists(upload_dir):
                os.makedirs(upload_dir)
            file.save(os.path.join(upload_dir, f"{safe_new_title}.{extension}"))
            update_fields['artikelPict'] = file_path
    
    # Update gambar author jika ada
    if 'fileAuthor' in request.files:
        fileAuthor = request.files['fileAuthor']
        if fileAuthor.filename:
            filename = secure_filename(fileAuthor.filename)
            extensionAuthor = filename.split('.')[-1]
            file_path_author = f"assets/img/authors/{safe_new_title}.{extensionAuthor}"
            upload_dir_author = os.path.join(current_app.root_path, "static", "assets", "img", "authors")
            if not os.path.exists(upload_dir_author):
                os.makedirs(upload_dir_author)
            fileAuthor.save(os.path.join(upload_dir_author, f"{safe_new_title}.{extensionAuthor}"))
            update_fields['authorPict'] = file_path_author
    
    # Update data di database
    result = current_app.db.artikel.update_one({'title': title}, {'$set': update_fields})
    
    if result.modified_count:
        return jsonify({'msg': 'Artikel berhasil diperbarui!', 'updated_fields': update_fields})
    else:
        return jsonify({'msg': 'Tidak ada perubahan atau artikel tidak ditemukan.'}), 400


@add_artikel_.route('/detail-artikel/<title>')
def detail_artikel(title):
    article = current_app.db.artikel.find_one({'title': title}, {'_id': False})
    if article:
        # Make sure konten is included in the response
        return jsonify({'msg': 'Artikel berhasil ditemukan!', 'article': article})
    return jsonify({'msg': 'Artikel tidak ditemukan'}), 404