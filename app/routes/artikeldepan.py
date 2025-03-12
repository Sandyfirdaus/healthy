from flask import Blueprint, render_template, request, redirect, url_for, current_app
import jwt

# Blueprint untuk halaman artikeldepan
artikeldepan_ = Blueprint('artikeldepan', __name__, template_folder='templates/dashboard')


@artikeldepan_.route('/artikeldepan')
def artikeldepan():
    articles = list(current_app.db.artikel.find({}, {'_id' : False}))    
    return render_template('dashboard/artikeldepan.html', articles=articles)
