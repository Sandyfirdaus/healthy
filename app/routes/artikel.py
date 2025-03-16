from flask import Blueprint, render_template, request, redirect, url_for, current_app
import jwt
import math

# Blueprint untuk halaman artikel
artikel_ = Blueprint('artikel', __name__, template_folder='templates/dashboard')

@artikel_.route('/artikel')
@artikel_.route('/artikel/<int:page>')
def artikel(page=1):
    myToken = request.cookies.get("mytoken")
    SECRET_KEY = current_app.config['SECRET_KEY']
    try:
        # Decode token dan ambil payload
        payload = jwt.decode(myToken, SECRET_KEY, algorithms=["HS256"])
        user_info = current_app.db.users.find_one({"username": payload["id"]})

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
        
        if not user_info:
            return redirect(url_for("home.menu"))

        return render_template('dashboard/artikel.html', 
                              articles=articles, 
                              user_info=user_info,
                              current_page=page,
                              total_pages=total_pages)
    except jwt.ExpiredSignatureError:
        return redirect(url_for("home.menu"))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("home.menu"))
    except Exception as e:
        # Log error untuk debugging (opsional)
        print(f"Error: {e}")
        return redirect(url_for("home.menu"))
