from flask import Flask, redirect, current_app, jsonify, url_for, render_template, Blueprint, request
import jwt
import urllib.parse

# Blueprint untuk halaman artikel
artikeldepan_details_ = Blueprint('artikeldepan_details', __name__, template_folder='templates/dashboard')


@artikeldepan_details_.route('/artikeldepan_details/<title>')
def artikel_detail(title):
    # Decode URL-encoded title
    decoded_title = urllib.parse.unquote(title)
    
    # Try to find the article with the decoded title
    article = current_app.db.artikel.find_one({'title': decoded_title}, {'_id': False})
    
    # If not found, try with the original title
    if not article:
        article = current_app.db.artikel.find_one({'title': title}, {'_id': False})
    
    if article:
        return render_template("dashboard/artikeldepan_details.html", article=article)
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
    app.register_blueprint(artikeldepan_details_, url_prefix='/artikeldepan_details')
    return app