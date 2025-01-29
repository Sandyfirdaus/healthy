from flask import Blueprint, render_template, request, redirect, url_for, current_app
import jwt

# Blueprint untuk halaman artikel
artikel_ = Blueprint('artikel', __name__, template_folder='templates/dashboard')

# Data untuk 6 artikel
articles = [
    {
        "id": "1",
        "image": "assets/img/artikel/artikel1.jpg",
        "category": "Mindfulness, Psychology",
        "title": "Apa Itu Mindfulness?",
        "author_image": "assets/img/authors/penulis1.jpg",
        "author": "Ratih Arruum Listiyandini",
        "date": "2022-08-23",
        "content_url": "/artikel/1"
    },
    {
        "id": "2",
        "image": "assets/img/artikel/artikel2.jpg",
        "category": "Psychology, Mindfulness,   Mindful",
        "title": "Cara Mudah Menjadi Mindful dalam Kehidupan Sehari-hari",
        "author_image": "assets/img/authors/penulis1.jpg",
        "author": "Ratih Arruum Listiyandini",
        "date": "2022-08-24",
        "content_url": "/artikel/2"
    },
    {
        "id": "3",
        "image": "assets/img/artikel/artikel3.jpg",
        "category": "Psychology, Mindfulness , Stress",
        "title": "Cara Efektif Mengatasi Stres: Hindari Lari, Hadapi dengan Mindfulness",
        "author_image": "assets/img/authors/penulis1.jpg",
        "author": "Ratih Arruum Listiyandini",
        "date": "2022-08-31",
        "content_url": "/artikel/3"
    },
    {
        "id": "4",
        "image": "assets/img/artikel/artikel4.jpg",
        "category": "Mindfulness, Psychology, Stress, Mahasiswa",
        "title": "Mahasiswa dan Stres: Tantangan yang Sering Dialamil",
        "author_image": "assets/img/authors/penulis1.jpg",
        "author": "Ratih Arruum Listiyandini",
        "date": "2022-08-30",
        "content_url": "/artikel/4"
    },
    {
        "id": "5",
        "image": "assets/img/artikel/artikel5.jpg",
        "category": "Mindfulness, Psychology, Anxiety, Inspirasi, Mediasosial",
        "title": "Media Sosial Hari Ini: Inspirasi atau Pemicu Kecemasan?",
        "author_image": "assets/img/authors/penulis1.jpg",
        "author": "Ratih Arruum Listiyandini",
        "date": "2023-11-15",
        "content_url": "/artikel/5"
    },
    {
        "id": "6",
        "image": "assets/img/artikel/artikel6.jpg",
        "category": "Psychology, Mindfulness, Tips, Trick, Newyear",
        "title": "Make Your Life Better: Tips dan Trik untuk Membangun Kebiasaan Baru yang Lebih Baik",
        "author_image": "assets/img/authors/penulis1.jpg",
        "author": "Ratih Arruum Listiyandini",
        "date": "2023-01-31",
        "content_url": "/artikel/6"
    }
]

@artikel_.route('/artikel')
def artikel():
    myToken = request.cookies.get("mytoken")
    SECRET_KEY = current_app.config['SECRET_KEY']
    try:
        # Decode token dan ambil payload
        payload = jwt.decode(myToken, SECRET_KEY, algorithms=["HS256"])
        user_info = current_app.db.users.find_one({"username": payload["id"]})

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
