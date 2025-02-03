from flask import Blueprint, render_template

# Blueprint untuk halaman artikeldepan
artikeldepan_ = Blueprint('artikeldepan', __name__, template_folder='templates/dashboard')

# Data untuk 6 artikeldepan
articles = [
    {
        "id": 1,
        "image": "/assets/img/artikel/artikel1.jpg",
        "category": "Mindfulness, Psychology",
        "title": "Apa Itu Mindfulness?",
        "author_image": "/assets/img/authors/penulis1.jpg",
        "author": "Ratih Arruum Listiyandini",
        "date": "2022-08-23",
        "content_url": "/artikeldepan/1"
    },
    {
        "id": 2,
        "image": "/assets/img/artikel/artikel2.jpg",
        "category": "Psychology, Mindfulness, Mindful",
        "title": "Cara Mudah Menjadi Mindful dalam Kehidupan Sehari-hari",
        "author_image": "/assets/img/authors/penulis1.jpg",
        "author": "Ratih Arruum Listiyandini",
        "date": "2022-08-24",
        "content_url": "/artikeldepan/2"
    },
    {
        "id": 3,
        "image": "/assets/img/artikel/artikel3.jpg",
        "category": "Psychology, Mindfulness, Stress",
        "title": "Cara Efektif Mengatasi Stres: Hindari Lari, Hadapi dengan Mindfulness",
        "author_image": "/assets/img/authors/penulis1.jpg",
        "author": "Ratih Arruum Listiyandini",
        "date": "2022-08-31",
        "content_url": "/artikeldepan/3"
    },
    {
        "id": 4,
        "image": "/assets/img/artikel/artikel4.jpg",
        "category": "Mindfulness, Psychology, Stress, Mahasiswa",
        "title": "Mahasiswa dan Stres: Tantangan yang Sering Dialami",
        "author_image": "/assets/img/authors/penulis1.jpg",
        "author": "Ratih Arruum Listiyandini",
        "date": "2022-08-30",
        "content_url": "/artikeldepan/4"
    },
    {
        "id": 5,
        "image": "/assets/img/artikel/artikel5.jpg",
        "category": "Mindfulness, Psychology, Anxiety, Inspirasi, Mediasosial",
        "title": "Media Sosial Hari Ini: Inspirasi atau Pemicu Kecemasan?",
        "author_image": "/assets/img/authors/penulis1.jpg",
        "author": "Ratih Arruum Listiyandini",
        "date": "2023-11-15",
        "content_url": "/artikeldepan/5"
    },
    {
        "id": 6,
        "image": "/assets/img/artikel/artikel6.jpg",
        "category": "Psychology, Mindfulness, Tips, Trick, Newyear",
        "title": "Make Your Life Better: Tips dan Trik untuk Membangun Kebiasaan Baru yang Lebih Baik",
        "author_image": "/assets/img/authors/penulis1.jpg",
        "author": "Ratih Arruum Listiyandini",
        "date": "2023-01-31",
        "content_url": "/artikeldepan/6"
    }
]

@artikeldepan_.route('/artikeldepan')
def artikeldepan():
    return render_template('dashboard/artikeldepan.html', articles=articles)
