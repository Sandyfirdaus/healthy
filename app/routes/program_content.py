from flask import Flask, request, redirect, url_for, current_app, render_template, Blueprint
from app.routes.program_details import materi_data  # Import materi_data from program_details
import jwt

program_content_ = Blueprint('program_content', __name__)

materi_data = {
    "1": {
        "judul": "Sesi 1 - Menjadi Sadar",
        "image": "assets/img/ilustrasi/sesi-1/Session 1.1.jpg",
    },
    "2": {
        "judul": "Sesi 2 - Memahami Pikiran Kamu",
        "image": "assets/img/ilustrasi/sesi-2/Session 2.1.jpg",
    },
    "3": {
        "judul": "Sesi 3 - Mengenali Hambatan dan Mendengarkan Tubuh",
        "image": "assets/img/ilustrasi/sesi-3/Ilustrasi 3.1.jpg",
    },
    "4": {
        "judul": "Sesi 4 - Mindfulness dalam Keseharian",
        "image": "assets/img/ilustrasi/sesi-4/Ilustrasi 4.1.jpg",
    }
}

@program_content_.route('/program_content')
def program_content():
    myToken = request.cookies.get("mytoken")
    SECRET_KEY = current_app.config['SECRET_KEY']
    try:
        payload = jwt.decode(myToken, SECRET_KEY, algorithms=["HS256"])
        user_info = current_app.db.users.find_one({"username": payload["id"]})
        return render_template('dashboard/program_content.html', materi_data=materi_data, user_info=user_info)  # Pass materi_data
    except jwt.ExpiredSignatureError:
        return redirect(url_for("home.menu"))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("home.menu"))
