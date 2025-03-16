from flask import Flask, redirect, current_app, jsonify, url_for, render_template, Blueprint, request
import jwt
import urllib.parse

# Blueprint untuk halaman artikel
artikel_details_ = Blueprint('artikel_details', __name__)

# Main route for article details with title parameter
@artikel_details_.route('/artikel_details/<title>')
def artikel_detail(title):  
    myToken = request.cookies.get("mytoken")
    
    # Decode URL-encoded title
    decoded_title = urllib.parse.unquote(title)
    
    # Try to find the article with the decoded title
    article = current_app.db.artikel.find_one({'title': decoded_title}, {'_id': False})
    
    # If not found, try with the original title
    if not article:
        article = current_app.db.artikel.find_one({'title': title}, {'_id': False})
    
    # If still not found, try adding a question mark
    if not article and not decoded_title.endswith('?'):
        article = current_app.db.artikel.find_one({'title': decoded_title + '?'}, {'_id': False})
    
    # If still not found, try with original title plus question mark
    if not article and not title.endswith('?'):
        article = current_app.db.artikel.find_one({'title': title + '?'}, {'_id': False})
    
    SECRET_KEY = current_app.config['SECRET_KEY']
    articles = current_app.db.artikel.find({}, {'_id': False})
    
    # If article is found, proceed with authentication
    if article:
        try:
            # Validasi token JWT
            payload = jwt.decode(myToken, SECRET_KEY, algorithms=["HS256"])
            user_info = current_app.db.users.find_one({"username": payload["id"]})
            
            return render_template("dashboard/artikel_details.html", article=article, user_info=user_info, articles=articles)
        except jwt.ExpiredSignatureError:
            # Token kadaluarsa
            return redirect(url_for("home.menu"))
        except jwt.exceptions.DecodeError:
            # Token tidak valid
            return redirect(url_for("home.menu"))
        except Exception as e:
            # Penanganan error umum
            return jsonify({"error": str(e)}), 500
    else:
        # For debugging
        print(f"Article not found: {title} (decoded: {decoded_title})")
        
        # Get all article titles from the database for comparison
        all_titles = [a.get('title') for a in current_app.db.artikel.find({}, {'title': 1, '_id': 0})]
        print(f"Available titles: {all_titles}")
        
        return render_template("dashboard/article_not_found.html", title=decoded_title), 404

# Define Blueprint in the main app
def create_app():
    app = Flask(__name__)
    app.register_blueprint(artikel_details_, url_prefix='/artikel_details')
    return app
