from flask import Blueprint, render_template, request, redirect, url_for, current_app
import jwt
import math

# Blueprint untuk halaman artikeldepan
artikeldepan_ = Blueprint('artikeldepan', __name__, template_folder='templates/dashboard')


@artikeldepan_.route('/artikeldepan')
@artikeldepan_.route('/artikeldepan/<int:page>')
def artikeldepan(page=1):
    # Pagination
    per_page = 6
    all_articles = list(current_app.db.artikel.find({}, {'_id': False}))
    total_articles = len(all_articles)
    total_pages = max(1, math.ceil(total_articles / per_page))  # Ensure at least 1 page
    
    # Ensure page is within valid range
    if page < 1:
        page = 1
    elif page > total_pages:
        page = total_pages
        
    # Calculate start and end indices for slicing
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    
    # Get articles for current page
    articles = all_articles[start_idx:end_idx] if all_articles else []
    
    return render_template('dashboard/artikeldepan.html', 
                          articles=articles,
                          current_page=page,
                          total_pages=total_pages)
