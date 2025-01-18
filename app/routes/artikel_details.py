from flask import Flask, redirect, current_app, jsonify, url_for, render_template, Blueprint, request
import jwt

# Blueprint untuk halaman artikel
artikel_details_ = Blueprint('artikel_details', __name__, template_folder='templates/dashboard')

# Data Artikel
articles = {
    "1": {
        "title": "Apa Itu Mindfulness?",
        "image": "assets/img/artikel/artikel1.jpg",
        "author": "Listiyandini, Ratih Arruum",
        "date": "23 Agustus 2022",
        "konten": 
            "Mindfulness adalah kemampuan untuk memberikan perhatian penuh terhadap berbagai pengalaman, baik internal maupun eksternal, tanpa memberikan penilaian."
            "Menurut definisi dari Kabat-Zinn (2003), mindfulness melibatkan perhatian terhadap pengalaman internal dan eksternal tanpa penghakiman.",
        "title_quotes": "Manfaat Mindfulness",
        "quotes": [
            "Mengurangi stres: Membantu menenangkan pikiran dan mengelola tekanan, Meningkatkan konsentrasi: Memperbaiki fokus dan perhatian terhadap tugas yang sedang dilakukan, Meningkatkan kesejahteraan emosional: Membantu mengelola emosi dengan lebih baik, menciptakan ketenangan, dan meningkatkan kebahagiaan."
        ],
        "title_isi": "Lima Ciri Mindfulness",
        "isi": [
            "Yang pertama Acting with Awareness (Bertindak dengan Kesadaran) Melakukan tindakan dengan penuh perhatian dan kesadaran. Ini berarti tidak menjalani hidup secara otomatis atau terburu-buru, melainkan dengan kesadaran penuh terhadap setiap tindakan.",
            "Yang Kedua Non-Judging (Tidak Menghakimi) Menghindari penilaian, baik positif maupun negatif, terhadap pengalaman yang dialami. Hal ini membantu menjaga netralitas dan menerima setiap momen tanpa prasangka.",
            "Yang ketiga Non-Reactivity (Tidak Reaktif) Tidak bereaksi secara impulsif terhadap situasi atau emosi yang muncul. Memberikan jeda sebelum merespons sesuatu, sehingga tindakan yang diambil lebih bijaksana.",
            "Yang keempat Describing (Menjelaskan dan Mengenali) Mengenali dan mendeskripsikan berbagai pengalaman, baik itu perasaan, pikiran, atau sensasi fisik, tanpa terjebak dalamnya. Ini membantu dalam memahami diri sendiri dengan lebih baik.",
            "Yang Terakhir Observing (Mengamati) Mengamati pengalaman internal dan eksternal secara objektif. Ini melibatkan perhatian penuh terhadap apa yang terjadi di sekitar kita, termasuk sensasi, suara, dan emosi",
        ],
        "title_akhir": "Keuntungan dari Melakukan Intervensi Berbasis Mindfulness",
        "akhir": [
            "Mengurangi stres: Membantu menenangkan pikiran dan mengelola tekanan.",
            "Meningkatkan konsentrasi: Memperbaiki fokus dan perhatian terhadap tugas yang sedang dilakukan.",
            "Meningkatkan kesejahteraan emosional: Membantu mengelola emosi dengan lebih baik, menciptakan ketenangan, dan meningkatkan kebahagiaan.",
            "Dengan melatih mindfulness, seseorang dapat lebih hadir dalam kehidupannya dan merespons tantangan dengan lebih tenang dan bijak.",
        ],
        "referensi": "Listiyandini, Ratih Arruum. (2021). A Guided Culturally-attuned Internet-delivered Mindfulness Intervention for Psychological Distress among Indonesian University Students. doi:10.13140/RG.2.2.33689.54882.",
        "tags": [
            "Mindfulness",
            "Psychology" 
        ],
        "penulis_foto": "assets/img/authors/penulis2.jpg",
        "penutup": "Intervensi mindfulness yang dirancang secara khusus dan disesuaikan dengan konteks budaya Indonesia, serta dipandu melalui internet, dapat menjadi strategi efektif untuk mengatasi tekanan psikologis yang dialami oleh remaja-dewasa di Indonesia."
    },
    "2":{
        "title": "Cara Mudah Menjadi Mindful dalam Kehidupan Sehari-hari",
        "image": "assets/img/artikel/artikel2.jpg",
        "author": "Ratih Arruum Listiyandini, M.Psi., Psikolog.",
        "date": "24 Agustus 2022",
        "konten": 
            "Pernahkah kamu merasa sibuk melakukan banyak hal sekaligus? Misalnya, makan sambil menonton film, mengikuti kelas sambil scrolling media sosial, atau menghadiri rapat online dengan dua perangkat sekaligus. Kebiasaan ini mungkin sudah menjadi bagian dari rutinitas kita, tetapi tahukah kamu bahwa hal tersebut adalah tanda bahwa kamu tidak menerapkan mindfulness dalam kehidupan sehari-hari?"
            "Mindfulness adalah kesadaran penuh terhadap apa yang sedang kita lakukan tanpa terdistraksi oleh pikiran atau kegiatan lain. Jon Kabat-Zinn, seorang ahli mindfulness, menjelaskan bahwa ada dua cara utama untuk mempraktikkan mindfulness dalam keseharian, yaitu melalui pendekatan formal dan informal.",
        "title_quotes": "Mengapa Mindfulness Penting?",
        "quotes": [
            "Mindfulness membantu kita keluar dari mode autopilot dan lebih sadar akan apa yang sedang terjadi di sekitar. Hal ini dapat meningkatkan kualitas hidup, mengurangi stres, serta meningkatkan konsentrasi."
        ],
        "title_isi": "Pendekatan Formal: Meditasi",
        "isi": [
            "Mindfulness secara formal dilakukan melalui meditasi, di mana fokus utama diarahkan pada napas dan tubuh.",
            "Meditasi tidak memerlukan waktu lama. Dengan melakukannya selama 5–10 menit setiap hari, kamu bisa mendapatkan manfaat berupa ketenangan pikiran dan fokus yang lebih tajam."
        ],
        "title_akhir": "Mulai Mindfulness Hari Ini",
        "akhir": [
            "Fokus pada satu aktivitas dalam satu waktu dan hindari multitasking.",
            "Pasang pengingat untuk meluangkan waktu sejenak bernapas dan menyadari momen.",
            "Latih kesabaran. Mindfulness adalah keterampilan yang memerlukan waktu dan konsistensi",
        ],
        "referensi": "Astin, J. A. (1997). Stress reduction through mindfulness meditation. Psychotherapy and Psychosomatics, 66(2), 97–106.",
        "tags": [
            "Mindfulness",
            "Psychology",
            "Mindful"
        ],
        "penulis_foto": "assets/img/authors/penulis2.jpg",
        "penutup": "Mindfulness membantu menjalani kehidupan dengan lebih sadar dan bahagia. Yuk, mulai hari ini!"
    },
    "3": {
       "title": "Cara Efektif Mengatasi Stres: Hindari Lari, Hadapi dengan Mindfulness",
       "image": "assets/img/artikel/artikel3.jpg",
       "author": "Ratih Arruum Listiyandini",
         "date": "25 Agustus 2022",
        "konten": 
            "Setiap orang pasti pernah merasa stres. Baik itu karena tekanan akademis, pekerjaan, atau masalah sehari-hari. Saat stres datang, wajar jika kita langsung mencari cara untuk keluar dari kondisi tersebut. Namun, pernahkah kamu bertanya, apakah cara yang kamu pilih sudah benar dan baik untuk dirimu sendiri? "
            "Ada berbagai pola perilaku individu dalam mengatasi stres. Berdasarkan penelitian, dua strategi utama sering digunakan: avoidant coping stress dan approach coping stress. Apa perbedaan keduanya, dan mana yang lebih ideal untuk dilakukan?",
        "title_quotes": "Mindfulness: Kunci Memilih Strategi yang Tepat",
        "quotes": [
            "Mindfulness dapat membantu kamu secara efektif memilih strategi approach coping stress. Mindfulness, atau kesadaran penuh, adalah kemampuan untuk fokus pada momen saat ini tanpa menghakimi. Dengan menerapkan mindfulness, seseorang lebih mampu menyadari apa yang sedang dirasakan, memahami penyebab stres, dan memilih cara yang sehat untuk menghadapinya."
        ],
        "title_isi": "Approach Coping Stress: Hadapi dan Selesaikan",
        "isi": [
        "Berpikir Proaktif: Menganalisis penyebab stres dan mencari solusi.",
        "Mengubah Perilaku: Berusaha menyesuaikan diri dengan situasi untuk mengurangi dampak stres.",
        "Berkomunikasi: Berbicara dengan orang lain untuk mendapatkan perspektif atau dukungan"
        ],
        "title_akhir": "Bagaimana Mempraktikkan Mindfulness untuk Mengurangi Stres?",
        "akhir": [
            "Latihan Pernapasan, Luangkan waktu sejenak untuk fokus pada napasmu. Tarik napas perlahan, hitung hingga empat, tahan selama empat detik, lalu hembuskan perlahan",
            "Mindful Observation, Luangkan waktu untuk memperhatikan hal-hal di sekitarmu, seperti suara burung, angin yang berhembus, atau sensasi tubuh saat duduk",
            "Refleksi Pikiran dan Emosi, Luangkan waktu untuk menyadari apa yang kamu rasakan. Jangan langsung bereaksi, tetapi coba amati dan pahami emosimu",
            "Mindful Walking, Ketika berjalan, fokus pada langkah kakimu, ritme pernapasanmu, dan bagaimana tubuhmu bergerak",
        ],
        "referensi": "Weinstein, N., Brown, K. W., & Ryan, R. M. (2009). A multi-method examination of the effects of mindfulness on stress attribution, coping, and emotional well-being. Journal of Research in Personality, 43(3), 374–385",
        "tags": [
            "Mindfulness",
            "Psychology"
            "Stress"
        ],
        "penulis_foto": "assets/img/authors/penulis2.jpg",
        "penutup": "Mindfulness tidak hanya memberikan manfaat psikologis tetapi juga mendukung keseimbangan hidup yang lebih holistik."
    },
    "4": {
        "title": "Mahasiswa dan Stres: Tantangan yang Sering Dialami",
        "image": "assets/img/artikel/artikel4.jpg",
        "author": "Ratih Arruum Listiyandini",
        "date": "26 Agustus 2022",
        "konten": 
            "Stres adalah reaksi tubuh terhadap perubahan yang membutuhkan respons, regulasi, atau adaptasi baik secara fisik, psikologis, maupun emosional (Silverman et al., 2010). Pada mahasiswa, stres sering kali berhubungan langsung dengan berbagai masalah yang dihadapi selama menjalani perkuliahan, seperti beban tugas akademik, kesulitan finansial, atau masalah adaptasi di lingkungan baru (Hunt & Eisenberg, 2010). "
            "Namun, tahukah kamu bahwa stres tidak selalu negatif? Dalam kadar rendah, stres justru dapat memberikan dampak positif, seperti meningkatkan motivasi dan produktivitas. Tetapi, jika stres menjadi berlebihan, hal ini dapat memicu berbagai masalah serius, baik secara biologis, psikologis, maupun sosial (Hidayati & Harsono, 2021).",
        "title_quotes": "Kesimpulan",
        "quotes": [
            "Stres adalah bagian dari kehidupan mahasiswa yang tidak bisa dihindari. Namun, dengan mengenali tanda-tanda stres, memahami penyebabnya, dan mengambil langkah untuk mengelolanya, kamu dapat mengubah stres menjadi peluang untuk tumbuh dan belajar. Ingat, stres bukanlah sesuatu yang harus kamu lawan sendirian. Dukungan dari orang lain dan penerapan strategi yang tepat dapat membantu kamu melewati masa-masa sulit ini"
        ],
        "title_isi": "Gejala Stres yang Perlu Diwaspadai",
        "isi": [
            "Jantung berdebar-debar.",
            "Lemas dan mudah lelah.",
            "Sakit kepala atau gangguan fisik lainnya.",
            "Gangguan tidur, seperti sulit tidur atau tidur terlalu banyak.",
            "Perubahan selera makan",
            "Mudah gelisah atau cemas.",
            "Suasana hati sering berubah-ubah.",
            "Tidak bersemangat untuk melakukan aktivitas sehari-hari.",
            "Kesulitan berkonsentrasi",
        ],
        "title_akhir": "Bagaimana Cara Mengelola Stres?",
        "akhir": [
            "Kenali Penyebab Stres. Identifikasi hal-hal yang menjadi pemicu stresmu. Apakah itu tugas yang menumpuk, konflik dengan teman, atau kesulitan beradaptasi?.",
            "Atur Prioritas. Buat daftar prioritas untuk tugas dan tanggung jawabmu. Fokuslah menyelesaikan yang paling penting terlebih dahulu.",
            "Praktikkan Mindfulness. Latih dirimu untuk lebih sadar akan momen saat ini. Mindfulness terbukti efektif membantu mahasiswa mengelola stres akademis dan memilih strategi coping yang lebih sehat (Hidayati & Harsono, 2021).",
            "Jaga Pola Hidup Sehat. Tidur yang cukup, makan makanan bergizi, dan olahraga teratur dapat membantu tubuhmu lebih tahan terhadap tekanan.",
            "Cari Dukungan Sosial. Bicaralah dengan teman, keluarga, atau konselor jika kamu merasa terlalu tertekan. Mendapatkan perspektif dari orang lain sering kali bisa membantu."
        ],
        "referensi": "Fauziyyah, R., Awinda, R. C., & Besral, B. (2021). Dampak Pembelajaran Jarak Jauh terhadap Tingkat Stres dan Kecemasan Mahasiswa selama Pandemi COVID-19. Jurnal Biostatistik, Kependudukan, Dan Informatika Kesehatan, 1(2), 113–123",
        "tags": [
            "Mindfulness",
            "Psychology",
            "Stress",
            "Mahasiswa"
        ],
        "penulis_foto": "assets/img/authors/penulis2.jpg",
        "penutup": "Memulai mindfulness tidak membutuhkan waktu lama atau alat khusus. Dengan konsistensi, kamu bisa merasakan manfaatnya."
        },
        "5": {
        "title": "Media Sosial Hari Ini: Inspirasi atau Pemicu Kecemasan?",
        "image": "assets/img/artikel/artikel5.jpg",
        "author": "Ratih Arruum Listiyandini",
        "date": "27 Agustus 2022",
        "konten": 
            "Media sosial kini menjadi bagian penting dari kehidupan kita sehari-hari, terutama di kalangan generasi muda. Platform seperti Instagram, TikTok, dan Twitter memungkinkan kita untuk terhubung, berbagi momen, dan mengekspresikan diri. Namun, di balik manfaatnya, media sosial juga memiliki dampak negatif yang bisa memengaruhi kesehatan mental, seperti memicu kecemasan dan rasa tidak percaya diri. Jadi, media sosial: inspirasi atau sumber kecemasan?",
        "title_quotes": "Kesimpulan",
        "quotes": [
            "Media sosial memiliki dua sisi yang saling bertolak belakang. Di satu sisi, ia dapat memicu kecemasan, terutama jika digunakan secara berlebihan atau tanpa kendali. Namun, di sisi lain, media sosial juga dapat menjadi sumber inspirasi dan ruang ekspresi yang memperkaya kehidupan kita.",
            "Kuncinya adalah bagaimana kita menggunakan media sosial dengan bijak. Dengan mengenali dampak negatifnya dan memanfaatkan sisi positifnya, kita dapat menjadikan media sosial sebagai alat untuk mendukung kesehatan mental, bukan sebagai sumber masalah."
        ],
        "title_isi": "Kebiasaan yang Memicu Anxiety di Media Sosial",
        "isi": [
            "Penggunaan Media Sosial Lebih dari 3 Jam Sehari. Studi menunjukkan bahwa menghabiskan waktu berlebihan di media sosial dapat meningkatkan risiko depresi dan kecemasan. Ini terjadi karena paparan yang terlalu sering terhadap konten negatif atau perbandingan sosial yang tidak sehat",
            "Rasa FOMO (Fear of Missing Out). Melihat kehidupan orang lain yang tampak sempurna di media sosial dapat memicu rasa takut ketinggalan atau FOMO. Hal ini membuat individu merasa cemas, rendah diri, bahkan iri, yang semakin memperburuk kondisi mental mereka.",
            "Ketergantungan pada Media Sosial. Individu dengan rasa percaya diri rendah cenderung lebih bergantung pada media sosial. Ketergantungan ini dapat menciptakan siklus kecemasan yang sulit dihentikan, karena individu terus-menerus mencari validasi melalui jumlah likes atau komentar",
        ],
        "title_akhir": "Bijak dalam Menggunakan Media Sosial",
        "akhir": [
            "Atur Waktu Penggunaan. Batasi waktu bermain media sosial agar tidak mengganggu keseimbangan aktivitas harianmu. Sebagai contoh, cobalah menggunakan fitur pengatur waktu di ponselmu.",
            "Pilih Konten yang Positif. Fokuslah mengikuti akun atau komunitas yang memberikan dampak positif, seperti edukasi, motivasi, atau hiburan sehat. Hindari konten yang membuatmu merasa tidak cukup baik.",
            "Kenali Batasan Diri. Jika kamu merasa cemas atau tertekan setelah menggunakan media sosial, jangan ragu untuk mengambil jeda. Beristirahat sejenak dari media sosial dapat membantu memperbaiki suasana hati dan kesehatan mentalmu.",
        ],
        "referensi": "Coe, E., Doy, A., Enomoto, K., & Healy, C. (2023). Gen Z mental health: The impact of tech and social media. McKinsey Health Institute",
        "tags": [
            "Mindfulness",
            "Psychology",
            "Anxiety",
            "Inspirasi",
            "Mediasosial"
        ],
        "penulis_foto": "assets/img/authors/penulis2.jpg",
        "penutup": "Produktivitas tidak hanya tentang kerja keras, tetapi juga tentang kerja cerdas melalui mindfulness."
    },
    "6": {
        "title": "Make Your Life Better: Tips dan Trik untuk Membangun Kebiasaan Baru yang Lebih Baik",
        "image": "assets/img/artikel/artikel6.jpg",
        "author": "Ratih Arruum Listiyandini",
        "date": "28 Agustus 2022",
        "konten": 
            "Kebiasaan adalah perilaku yang dilakukan secara otomatis karena sering dilatih dan diulang. Ketika kita memiliki kebiasaan baik, otak akan bekerja lebih efisien karena perilaku tersebut menjadi bagian dari rutinitas harian. "
            "Misalnya, ketika kamu membiasakan diri untuk membaca 10 menit setiap hari, tanpa terasa, kamu akan menjadi pribadi yang lebih teredukasi. Begitu pula dengan kebiasaan sehat seperti berolahraga, tidur cukup, atau minum air putih secara teratur. Kebiasaan kecil ini, jika dilakukan konsisten, akan membawa perubahan besar dalam jangka panjang. "
            "Namun, memang tidak mudah untuk memulai dan tetap konsisten dalam membangun kebiasaan baru. Lalu, bagaimana cara melakukannya?",
        "title_quotes": "Kesimpulan",
        "quotes": [
            "Tahun baru adalah kesempatan untuk memulai hal-hal baru yang lebih baik. Dengan kebiasaan yang baik, kamu bisa meningkatkan kualitas hidupmu secara perlahan namun pasti.",
            "Ingat, mulailah dari hal kecil, tetap konsisten, dan pahami manfaat dari kebiasaan yang ingin dibangun. Dengan demikian, kebiasaan tersebut akan menjadi bagian dari dirimu dan membuat hidupmu lebih baik. Jadi, yuk, jadikan tahun ini momen untuk menjadi versi terbaik dari dirimu sendiri"
        ],
        "title_isi": "Tips dan Trik Membangun Kebiasaan Baru",
        "isi": [
            "Buat Rencana yang Jelas. Tentukan aktivitas baru yang ingin kamu lakukan dan buat rencana yang spesifik. Misalnya, jika ingin mulai berolahraga, tuliskan jadwal, durasi, dan jenis olahraga yang akan dilakukan. Dengan rencana yang jelas, kamu akan lebih mudah untuk memulainya.",
            "Mulai dari Hal yang Kecil dan Mudah. Jangan langsung membuat target besar yang sulit dicapai. Mulailah dari kebiasaan kecil. Contohnya, jika ingin membaca buku, mulailah dengan membaca satu halaman per hari. Ketika kebiasaan kecil ini sudah terbentuk, kamu bisa meningkatkan intensitas atau durasinya.",
            "Tetap Konsisten. Kunci utama membangun kebiasaan adalah konsistensi. Buatlah kebiasaan tersebut menjadi bagian dari rutinitas harianmu. Misalnya, jika ingin mulai meditasi, lakukan setiap pagi sebelum beraktivitas. Konsistensi akan membuat otak terbiasa dan menjadikan kebiasaan itu lebih mudah dilakukan",
            "Pahami Keuntungan dari Kebiasaan Baru. Ketika kamu tahu manfaat dari kebiasaan yang ingin dibangun, motivasimu akan meningkat. Misalnya, berolahraga secara rutin dapat meningkatkan energi, memperbaiki suasana hati, dan membuat tubuh lebih sehat. Dengan memahami manfaatnya, kamu akan lebih semangat untuk terus melakukannya",
            "Sabar dan Beri Waktu pada Dirimu Sendiri. Ingat, perubahan tidak terjadi dalam semalam. Dibutuhkan waktu dan kesabaran untuk menjadikan sesuatu sebagai kebiasaan. Jangan menyerah jika kamu gagal melakukannya beberapa kali. Bangkit dan terus coba lagi.",
        ],
        "title_akhir": "Manfaat Membangun Kebiasaan Baik",
        "akhir": [
            "Produktivitas meningkat: Dengan kebiasaan yang baik, seperti merencanakan jadwal harian, kamu dapat menyelesaikan lebih banyak hal dengan efisien.",
            "Kesehatan fisik dan mental yang lebih baik: Kebiasaan seperti tidur cukup, olahraga, dan makan sehat dapat meningkatkan kualitas hidup.",
            "Peningkatan rasa percaya diri: Kebiasaan baik membuatmu merasa lebih disiplin dan mampu mengendalikan hidupmu sendiri."
        ],
        "referensi": "https://www.gurusukses.com/pentingnya-membiasakan-diri-dengan-kebiasaan-yang-baik",
        "tags": [
            "Psychology",
            "Mindfulness",
            "Tips",
            "Trick",
            "Newyear"
        ],
        "penulis_foto": "assets/img/authors/penulis2.jpg",
        "penutup": "Mindfulness adalah alat penting bagi generasi digital untuk menjaga keseimbangan dalam dunia yang serba cepat."
    }
}

data = [
    {
        "id": "1",
        "image": "assets/img/artikel/artikel1.jpg",
        "category": "Mindfulness, Psychology",
        "title": "Apa Itu Mindfulness?",
        "author_image": "assets/img/authors/penulis2.jpg",
        "author": "Ratih Arruum Listiyandini, M.Psi., Psikolog.",
        "date": "2022-08-23",
        "content_url": "/artikel/1"
    },
    {
        "id": "2",
        "image": "assets/img/artikel/artikel2.jpg",
        "category": "Psychology, Mindfulness,   Mindful",
        "title": "Cara Mudah Menjadi Mindful dalam Kehidupan Sehari-hari",
        "author_image": "assets/img/authors/penulis2.jpg",
        "author": "Ratih Arruum Listiyandini, M.Psi., Psikolog.",
        "date": "2022-08-24",
        "content_url": "/artikel/2"
    },
    {
        "id": "3",
        "image": "assets/img/artikel/artikel3.jpg",
        "category": "Psychology, Mindfulness , Stress",
        "title": "Cara Efektif Mengatasi Stres: Hindari Lari, Hadapi dengan Mindfulness",
        "author_image": "assets/img/authors/penulis2.jpg",
        "author": "Ratih Arruum Listiyandini, M.Psi., Psikolog.",
        "date": "2022-08-31",
        "content_url": "/artikel/3"
    },
    {
        "id": "4",
        "image": "assets/img/artikel/artikel4.jpg",
        "category": "Mindfulness, Psychology, Stress, Mahasiswa",
        "title": "Mahasiswa dan Stres: Tantangan yang Sering Dialamil",
        "author_image": "assets/img/authors/penulis2.jpg",
        "author": "Ratih Arruum Listiyandini, M.Psi., Psikolog.",
        "date": "2022-08-30",
        "content_url": "/artikel/4"
    },
    {
        "id": "5",
        "image": "assets/img/artikel/artikel5.jpg",
        "category": "Mindfulness, Psychology, Anxiety, Inspirasi, Mediasosial",
        "title": "Media Sosial Hari Ini: Inspirasi atau Pemicu Kecemasan?",
        "author_image": "assets/img/authors/penulis2.jpg",
        "author": "Ratih Arruum Listiyandini, M.Psi., Psikolog.",
        "date": "2023-11-15",
        "content_url": "/artikel/5"
    },
    {
        "id": "6",
        "image": "assets/img/artikel/artikel6.jpg",
        "category": "Psychology, Mindfulness, Tips, Trick, Newyear",
        "title": "Make Your Life Better: Tips dan Trik untuk Membangun Kebiasaan Baru yang Lebih Baik",
        "author_image": "assets/img/authors/penulis2.jpg",
        "author": "Ratih Arruum Listiyandini, M.Psi., Psikolog.",
        "date": "2023-01-31",
        "content_url": "/artikel/6"
    }
]

@artikel_details_.route('/artikel_details/<int:article_id>')  # Change to article_id here
def artikel_detail(article_id):  # Also change to article_id here
    article_id = str(article_id)
    article = articles.get(article_id)
    myToken = request.cookies.get("mytoken")
    SECRET_KEY = current_app.config['SECRET_KEY']
    
    try:
        # Validasi token JWT
        payload = jwt.decode(myToken, SECRET_KEY, algorithms=["HS256"])
        user_info = current_app.db.users.find_one({"username": payload["id"]})
        
        # Jika artikel ditemukan, render template
        if article:
            return render_template("dashboard/artikel_details.html", article=article, user_info=user_info, articles=data)
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
