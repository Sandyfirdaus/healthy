from flask import Flask, request, render_template, current_app, Blueprint, jsonify, redirect, url_for, make_response
import jwt

home_ = Blueprint('home', __name__)

@home_.route('/home')
def menu():
    return render_template('dashboard/home.html')

@home_.route('/')
def home():
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