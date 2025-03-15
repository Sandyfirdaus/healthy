from flask import Flask, request, redirect, url_for, current_app, render_template, Blueprint
import jwt

program_content_ = Blueprint('program_content', __name__)

@program_content_.route('/program_content/<program_title>')
def program_content(program_title):
    myToken = request.cookies.get("mytoken")
    SECRET_KEY = current_app.config['SECRET_KEY']
    try:
        payload = jwt.decode(myToken, SECRET_KEY, algorithms=["HS256"])
        user_info = current_app.db.users.find_one({"username": payload["id"]})
        
        # Fetch materials for this specific program from database
        materials = list(current_app.db.materi.find({"program_title": program_title}, {'_id': False}))
        
        # Convert materials list to the format expected by the template
        materi_data = {}
        for i, materi in enumerate(materials, 1):
            materi_data[str(i)] = {
                "judul": materi["title"],
                "title": materi["title"],
                "image": materi.get("coverImage", "assets/img/default.jpg")
            }
        
        return render_template('dashboard/program_content.html', 
                            materi_data=materi_data, 
                            user_info=user_info,
                            program_title=program_title)
    except jwt.ExpiredSignatureError:
        return redirect(url_for("home.menu"))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("home.menu"))
