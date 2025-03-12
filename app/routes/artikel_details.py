from flask import Flask, redirect, current_app, jsonify, url_for, render_template, Blueprint, request
import jwt

# Blueprint untuk halaman artikel
artikel_details_ = Blueprint('artikel_details', __name__, template_folder='templates/dashboard')


@artikel_details_.route('/artikel_details/<title>')  # Change to article_id here
def artikel_detail(title):  
    myToken = request.cookies.get("mytoken")
    article = current_app.db.artikel.find_one({'title': title}, {'_id' : False})
    SECRET_KEY = current_app.config['SECRET_KEY']
    articles = current_app.db.artikel.find({}, {'_id': False})
    try:
        # Validasi token JWT
        payload = jwt.decode(myToken, SECRET_KEY, algorithms=["HS256"])
        user_info = current_app.db.users.find_one({"username": payload["id"]})
        
        # Jika artikel ditemukan, render template
        if article:
            return render_template("dashboard/artikel_details.html", article=article, user_info=user_info, articles=articles)
        else:
            return "Artikel tidak ditemukan", 404
    except jwt.ExpiredSignatureError:
        # Token kadaluarsa
        return redirect(url_for("home.menu"))
    except jwt.exceptions.DecodeError:
        # Token tidak valid
        return redirect(url_for("home.menu"))
    except Exception as e:
        # Penanganan error umum
        return jsonify({"error": str(e)}), 500

# Define Blueprint in the main app
def create_app():
    app = Flask(__name__)
    app.register_blueprint(artikel_details_, url_prefix='/artikel_details')
    return app
