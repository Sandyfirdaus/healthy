from flask import Flask, redirect, current_app, jsonify, url_for, render_template, Blueprint, request
import jwt

# Blueprint untuk halaman artikel
artikeldepan_details_ = Blueprint('artikeldepan_details', __name__, template_folder='templates/dashboard')


@artikeldepan_details_.route('/artikeldepan_details/<title>')  # Change to article_id here
def artikel_detail(title):  # Also change to article_id here
    article = current_app.db.artikel.find_one({'title': title}, {'_id' : False})

    if article:
        return render_template("dashboard/artikeldepan_details.html", article=article)
    else:
        return "Artikel tidak ditemukan", 404

# Define Blueprint in the main app
def create_app():
    app = Flask(__name__)
    app.register_blueprint(artikeldepan_details_, url_prefix='/artikeldepan_details')
    return app