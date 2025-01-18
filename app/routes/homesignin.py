from flask import Flask, redirect, url_for, request, request, render_template, current_app, render_template, Blueprint
import jwt

homesignin_ = Blueprint('homesignin', __name__)

@homesignin_.route('/homesignin')
def homesignin():
    myToken = request.cookies.get("mytoken")
    SECRET_KEY = current_app.config['SECRET_KEY']
    try:
        payload = jwt.decode(myToken, SECRET_KEY, algorithms=["HS256"])
        user_info = current_app.db.users.find_one({"username": payload["id"]})
        return render_template('dashboard/homesignin.html', user_info=user_info)
    except jwt.ExpiredSignatureError:
        return redirect(url_for("home.menu"))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("home.menu"))