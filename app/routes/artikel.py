from flask import Blueprint, render_template, request, redirect, url_for, current_app
import jwt

# Blueprint untuk halaman artikel
artikel_ = Blueprint('artikel', __name__, template_folder='templates/dashboard')

@artikel_.route('/artikel')
def artikel():
    myToken = request.cookies.get("mytoken")
    SECRET_KEY = current_app.config['SECRET_KEY']
    try:
        # Decode token dan ambil payload
        payload = jwt.decode(myToken, SECRET_KEY, algorithms=["HS256"])
        user_info = current_app.db.users.find_one({"username": payload["id"]})

        articles = list(current_app.db.artikel.find({}, {'_id' : False}))    
        if not user_info:
            return redirect(url_for("home.menu"))

        return render_template('dashboard/artikel.html', articles=articles, user_info=user_info)  # Pass articles dan user_info
    except jwt.ExpiredSignatureError:
        return redirect(url_for("home.menu"))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("home.menu"))
    except Exception as e:
        # Log error untuk debugging (opsional)
        print(f"Error: {e}")
        return redirect(url_for("home.menu"))
