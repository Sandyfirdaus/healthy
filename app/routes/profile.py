from flask import Flask, request, render_template, current_app, Blueprint, jsonify, redirect, url_for
from werkzeug.utils import secure_filename
import jwt
import os
from bson import json_util, ObjectId

profile_ = Blueprint('profile', __name__)

@profile_.route('/profile')
def profile():
    myToken = request.cookies.get("mytoken")
    SECRET_KEY = current_app.config['SECRET_KEY']
    try:
        payload = jwt.decode(myToken, SECRET_KEY, algorithms=["HS256"])
        user_info = current_app.db.users.find_one({"username": payload["id"]})
        namaLengkap = user_info.get("namaLengkap")
        testimoni = current_app.db.testimoni.find_one({"namaLengkap": namaLengkap})
        
        return render_template('profile/profile.html', user_info=user_info, testimoni=testimoni)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home.menu"))
    
@profile_.route('/update-profile', methods=["POST"])
def update_profile():
    SECRET_KEY = current_app.config['SECRET_KEY']
    token_receive = request.cookies.get("mytoken")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        username = payload["id"]
        newDoc = {}

        if "filePict" in request.files:
            file = request.files["filePict"]
            if file.filename != '':  # Ensure file has a valid filename
                filename = secure_filename(file.filename)
                extension = filename.split(".")[-1]
                file_path = f"assets/img/profile/{username}.{extension}"

                # Ensure the directory exists
                upload_dir = os.path.join(current_app.root_path, "static", "assets", "img", "profile")
                if not os.path.exists(upload_dir):
                    os.makedirs(upload_dir)

                # Save file to the server
                file.save(os.path.join(upload_dir, f"{username}.{extension}"))

                # Add the new profile picture details to the document
                newDoc["profile"] = filename
                newDoc["profilePict"] = file_path

        # Update user in the database
        current_app.db.users.update_one({"username": username}, {"$set": newDoc})

        return jsonify({"msg": "Profile successfully updated!"})

    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        # Handle expired or invalid JWT token
        return redirect(url_for("dashboard"))

    except Exception as e:
        # Catch any other unexpected errors
        print(f"Error: {e}")  # You can also use logging for more robust error tracking
        return jsonify({"msg": "An error occurred while updating the profile."}), 500
    
    
@profile_.route('/rating', methods=["POST"])
def rating():
    SECRET_KEY = current_app.config['SECRET_KEY']
    token_receive = request.cookies.get("mytoken")
    payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
    username = payload["id"]
    namaLengkap = request.form['namaLengkap']
    star = request.form['star']
    foto = request.form['foto']
    testimonial = request.form['testimonial']
    
    doc = {
        'namaLengkap': namaLengkap,
        'star': star,
        'foto': foto,
        'testimonial': testimonial,
    }
    current_app.db.users.update_one({"username": username}, {"$set": {"testimoni": "done"}})
    current_app.db.testimoni.insert_one(doc)
    
    return jsonify({'msg': "success"})

@profile_.route('/update-rating', methods=["POST"])
def update_rating():
    namaLengkap = request.form['namaLengkap']
    star = request.form['star']
    foto = request.form['foto']
    testimonial = request.form['testimonial']
    
    newDoc = {
        'namaLengkap': namaLengkap,
        'star': star,
        'foto': foto,
        'testimonial': testimonial,
    }
    
    current_app.db.testimoni.update_one({"namaLengkap": namaLengkap}, {"$set": newDoc})
    return jsonify({'msg': "success"})
    
@profile_.route('/rating', methods=["GET"])
def get_rating():
    testimonial = list(current_app.db.testimoni.find({},{'_id':False}))
    return jsonify({'testimonial':testimonial})

@profile_.route('/check-status', methods=["GET"])
def check_status():
    myToken = request.cookies.get("mytoken")
    SECRET_KEY = current_app.config['SECRET_KEY']
    # Decode JWT
    payload = jwt.decode(myToken, SECRET_KEY, algorithms=["HS256"])
        
    # Akses koleksi 'status'
    progres = list(current_app.db.status.find({'username': payload["id"]}, {'_id' : False}))
        
    # Return hasil
    return jsonify({"progres": progres})
