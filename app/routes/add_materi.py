from flask import Flask, request, render_template, current_app, Blueprint, jsonify, redirect, url_for
from werkzeug.utils import secure_filename
import jwt
import os
import subprocess
from speech_recognition import Recognizer, AudioFile, UnknownValueError, RequestError
import tempfile
from pydub import AudioSegment
import json
from datetime import timedelta
import wave
import shutil
import datetime
try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

# Konfigurasi path ffmpeg
FFMPEG_PATH = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'utils', 'ffmpeg'))
FFMPEG_EXE = os.path.join(FFMPEG_PATH, 'ffmpeg.exe')
FFPROBE_EXE = os.path.join(FFMPEG_PATH, 'ffprobe.exe')

# Check if we're on Windows or Linux/Mac
if os.name == 'nt':  # Windows
    if not os.path.exists(FFMPEG_EXE):
        # Try to find ffmpeg in PATH
        try:
            FFMPEG_EXE = shutil.which('ffmpeg.exe') or shutil.which('ffmpeg')
            FFPROBE_EXE = shutil.which('ffprobe.exe') or shutil.which('ffprobe')
            if FFMPEG_EXE:
                FFMPEG_PATH = os.path.dirname(FFMPEG_EXE)
                print(f"Found FFmpeg in PATH: {FFMPEG_EXE}")
        except Exception as e:
            print(f"Error finding FFmpeg in PATH: {str(e)}")
else:  # Linux/Mac
    FFMPEG_EXE = os.path.join(FFMPEG_PATH, 'ffmpeg')
    FFPROBE_EXE = os.path.join(FFMPEG_PATH, 'ffprobe')
    
    if not os.path.exists(FFMPEG_EXE):
        # Try to find ffmpeg in PATH
        try:
            FFMPEG_EXE = shutil.which('ffmpeg')
            FFPROBE_EXE = shutil.which('ffprobe')
            if FFMPEG_EXE:
                FFMPEG_PATH = os.path.dirname(FFMPEG_EXE)
                print(f"Found FFmpeg in PATH: {FFMPEG_EXE}")
        except Exception as e:
            print(f"Error finding FFmpeg in PATH: {str(e)}")

if os.path.exists(FFMPEG_PATH) and os.path.exists(FFMPEG_EXE) and os.path.exists(FFPROBE_EXE):
    os.environ["PATH"] = FFMPEG_PATH + os.pathsep + os.environ["PATH"]
    AudioSegment.converter = FFMPEG_EXE
    AudioSegment.ffmpeg = FFMPEG_EXE
    AudioSegment.ffprobe = FFPROBE_EXE
    print(f"FFmpeg path configured: {FFMPEG_PATH}")
    print(f"FFmpeg executable: {FFMPEG_EXE}")
    print(f"FFprobe executable: {FFPROBE_EXE}")
else:
    print("Warning: FFmpeg files not found!")
    print(f"Looking in: {FFMPEG_PATH}")
    print(f"Files exist? ffmpeg.exe: {os.path.exists(FFMPEG_EXE)}, ffprobe.exe: {os.path.exists(FFPROBE_EXE)}")
    
    # Try to use system ffmpeg as a last resort
    try:
        if shutil.which('ffmpeg'):
            print("Using system FFmpeg")
            AudioSegment.converter = shutil.which('ffmpeg')
            AudioSegment.ffmpeg = shutil.which('ffmpeg')
            AudioSegment.ffprobe = shutil.which('ffprobe')
    except Exception as e:
        print(f"Error configuring system FFmpeg: {str(e)}")

add_materi_ = Blueprint('add_materi', __name__)

@add_materi_.route('/add-materi')
def view_materi():
    myToken = request.cookies.get("mytoken")
    SECRET_KEY = current_app.config['SECRET_KEY']
    try:
        payload = jwt.decode(myToken, SECRET_KEY, algorithms=["HS256"])
        user_info = current_app.db.users_admin.find_one({"username": payload["id"]})

        if user_info and user_info.get('username') == 'admin.psidamai':
            return render_template('dashboard_admin/add_materi.html', user_info=user_info)
        else:
            return redirect(url_for("auth_admin.login_admin"))
        
    except jwt.ExpiredSignatureError:
        return redirect(url_for("auth_admin.login_admin"))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("auth_admin.login_admin"))

@add_materi_.route('/get-materi', methods=['GET'])
def get_materi():
    data_materi = list(current_app.db.materi.find({}, {'_id': False}))
    return jsonify({"data_materi": data_materi})

@add_materi_.route('/add-materi/<program_title>', methods=['POST'])
def add_program_materi(program_title):
    try:
        # Ensure default cover exists
        ensure_directories_exist()
        ensure_default_cover_exists()
        
        # Get data from form
        title = request.form.get('title')
        description = request.form.get('description')
        
        # Validate required fields
        if not title or not program_title:
            return jsonify({'success': False, 'msg': 'Judul dan program wajib diisi'}), 400
        
        # Pastikan UPLOAD_FOLDER ada dalam konfigurasi
        if not hasattr(current_app.config, 'UPLOAD_FOLDER'):
            # Jika tidak ada, gunakan direktori static/assets
            current_app.config['UPLOAD_FOLDER'] = os.path.join(current_app.root_path, 'static', 'assets')
            print(f"UPLOAD_FOLDER not found in config, using: {current_app.config['UPLOAD_FOLDER']}")
        
        # Create program-specific directories if they don't exist
        program_dir = os.path.join(current_app.root_path, 'static', 'assets', 'programs', program_title.replace(' ', '_').lower())
        program_img_dir = os.path.join(program_dir, 'img')
        program_pdf_dir = os.path.join(program_dir, 'pdf')
        program_audio_dir = os.path.join(program_dir, 'audio')
        
        for directory in [program_dir, program_img_dir, program_pdf_dir, program_audio_dir]:
            if not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
                print(f"Created directory: {directory}")
        
        # Process cover image
        cover_image_path = None
        if 'coverImage' in request.files and request.files['coverImage'].filename:
            try:
                cover_file = request.files['coverImage']
                cover_image_filename = secure_filename(f"{title.replace(' ', '_').lower()}_cover{os.path.splitext(cover_file.filename)[1]}")
                cover_file.save(os.path.join(program_img_dir, cover_image_filename))
                cover_image_path = f"assets/programs/{program_title.replace(' ', '_').lower()}/img/{cover_image_filename}"
                print(f"Saved cover image: {cover_image_filename}")
            except Exception as e:
                print(f"Error saving cover image: {str(e)}")
                # Use default cover if there's an error
                cover_image_path = 'default_cover.jpg'
        else:
            # Use default cover if no image is provided
            cover_image_path = 'default_cover.jpg'
        
        # Process summary PDF
        summary_pdf_path = None
        if 'summaryPdf' in request.files and request.files['summaryPdf'].filename:
            try:
                pdf_file = request.files['summaryPdf']
                pdf_filename = secure_filename(f"{title.replace(' ', '_').lower()}_summary{os.path.splitext(pdf_file.filename)[1]}")
                pdf_file.save(os.path.join(program_pdf_dir, pdf_filename))
                summary_pdf_path = f"assets/programs/{program_title.replace(' ', '_').lower()}/pdf/{pdf_filename}"
                print(f"Saved PDF: {pdf_filename}")
            except Exception as e:
                print(f"Error saving PDF: {str(e)}")
        
        # Process journal link
        journal_link = request.form.get('journalLink', '')
        
        # Process relaxation audios
        relaxation_audios = []
        for i in range(1, 3):  # For audioRelaxation1 and audioRelaxation2
            audio_key = f'audioRelaxation{i}'
            if audio_key in request.files and request.files[audio_key].filename:
                try:
                    audio_file = request.files[audio_key]
                    audio_filename = secure_filename(f"{title.replace(' ', '_').lower()}_relaxation_{i}{os.path.splitext(audio_file.filename)[1]}")
                    audio_file.save(os.path.join(program_audio_dir, audio_filename))
                    relaxation_audios.append(f"assets/programs/{program_title.replace(' ', '_').lower()}/audio/{audio_filename}")
                    print(f"Saved relaxation audio {i}: {audio_filename}")
                except Exception as e:
                    print(f"Error saving relaxation audio {i}: {str(e)}")
        
        # Process learning audios and subtitles
        learning_audios = []
        audio_subtitles = []
        
        for i in range(9):  # Maximum 9 learning audios
            audio_key = f'learningAudio_{i}'
            subtitle_key = f'audioSubtitle_{i}'
            
            if audio_key in request.files and request.files[audio_key].filename:
                try:
                    audio_file = request.files[audio_key]
                    audio_filename = secure_filename(f"{title.replace(' ', '_').lower()}_learning_{i}{os.path.splitext(audio_file.filename)[1]}")
                    audio_file.save(os.path.join(program_audio_dir, audio_filename))
                    learning_audios.append(f"assets/programs/{program_title.replace(' ', '_').lower()}/audio/{audio_filename}")
                    
                    # Get corresponding subtitle if available
                    subtitle = request.form.get(subtitle_key, '')
                    audio_subtitles.append(subtitle)
                    print(f"Saved learning audio {i}: {audio_filename}")
                except Exception as e:
                    print(f"Error saving learning audio {i}: {str(e)}")
        
        # Process illustrations
        illustrations = []
        for i in range(9):  # Maximum 9 illustrations
            illustration_key = f'illustration_{i}'
            if illustration_key in request.files and request.files[illustration_key].filename:
                try:
                    illustration_file = request.files[illustration_key]
                    illustration_filename = secure_filename(f"{title.replace(' ', '_').lower()}_illustration_{i}{os.path.splitext(illustration_file.filename)[1]}")
                    illustration_file.save(os.path.join(program_img_dir, illustration_filename))
                    illustrations.append(f"assets/programs/{program_title.replace(' ', '_').lower()}/img/{illustration_filename}")
                    print(f"Saved illustration {i}: {illustration_filename}")
                except Exception as e:
                    print(f"Error saving illustration {i}: {str(e)}")
        
        # Create document for MongoDB
        materi_doc = {
            'title': title,
            'description': description,
            'program_title': program_title,
            'coverImage': cover_image_path,
            'summary_pdf': summary_pdf_path,
            'journal': journal_link,
            'relaxation_audios': relaxation_audios,
            'learning_audios': learning_audios,
            'audio_subtitles': audio_subtitles,
            'illustrations': illustrations,
            'created_at': datetime.datetime.now()
        }
        
        # Insert to MongoDB
        current_app.db.materi.insert_one(materi_doc)
        
        return jsonify({'success': True, 'msg': 'Materi berhasil ditambahkan'})
    except Exception as e:
        print(f"Error in add_program_materi: {str(e)}")
        return jsonify({'success': False, 'msg': f'Terjadi kesalahan: {str(e)}'}), 500

@add_materi_.route('/get-program-materi/<program_title>', methods=['GET'])
def get_program_materi(program_title):
    data_materi = list(current_app.db.materi.find(
        {'program_title': program_title}, 
        {'_id': False}
    ))
    return jsonify({"data_materi": data_materi})

@add_materi_.route('/delete-materi', methods=['POST'])
def delete_materi():
    try:
        title = request.form.get('title')
        program_title = request.form.get('program_title')
        
        if not title or not program_title:
            return jsonify({'msg': 'Title dan program_title diperlukan!'}), 400
        
        print(f"Attempting to delete materi: {title} from program: {program_title}")
        
        # Check if the materi exists
        materi = current_app.db.materi.find_one({
            'title': title,
            'program_title': program_title
        })
        
        if not materi:
            return jsonify({'msg': f'Materi dengan judul "{title}" tidak ditemukan!'}), 404
        
        # Try to delete associated files
        try:
            # Delete cover image if it exists
            if 'coverImage' in materi:
                if materi['coverImage'] == 'default_cover.jpg':
                    # Skip deleting default cover
                    pass
                elif materi['coverImage'].startswith('assets/'):
                    # If it's a full path (new format)
                    cover_path = os.path.join(current_app.root_path, "static", materi['coverImage'])
                    if os.path.exists(cover_path):
                        os.remove(cover_path)
                        print(f"Deleted cover image: {cover_path}")
                else:
                    # If it's just a filename (legacy format)
                    cover_path = os.path.join(current_app.root_path, "static", "assets", "img", "materi", materi['coverImage'])
                    if os.path.exists(cover_path):
                        os.remove(cover_path)
                        print(f"Deleted cover image: {cover_path}")
            
            # Delete illustration images if they exist
            if 'illustrations' in materi and isinstance(materi['illustrations'], list):
                for illustration in materi['illustrations']:
                    ill_path = os.path.join(current_app.root_path, "static", illustration)
                    if os.path.exists(ill_path):
                        os.remove(ill_path)
                        print(f"Deleted illustration: {ill_path}")
            
            # Delete audio files if they exist
            if 'relaxation_audios' in materi and isinstance(materi['relaxation_audios'], list):
                for audio in materi['relaxation_audios']:
                    audio_path = os.path.join(current_app.root_path, "static", audio)
                    if os.path.exists(audio_path):
                        os.remove(audio_path)
                        print(f"Deleted audio: {audio_path}")
            
            # Delete learning audio files if they exist
            if 'learning_audios' in materi and isinstance(materi['learning_audios'], list):
                for audio in materi['learning_audios']:
                    audio_path = os.path.join(current_app.root_path, "static", audio)
                    if os.path.exists(audio_path):
                        os.remove(audio_path)
                        print(f"Deleted learning audio: {audio_path}")
            
            # Delete summary PDF if it exists
            if 'summary_pdf' in materi and materi['summary_pdf']:
                pdf_path = os.path.join(current_app.root_path, "static", materi['summary_pdf'])
                if os.path.exists(pdf_path):
                    os.remove(pdf_path)
                    print(f"Deleted summary PDF: {pdf_path}")
        except Exception as file_error:
            print(f"Warning: Error deleting files: {str(file_error)}")
            # Continue with database deletion even if file deletion fails
        
        # Delete the materi from database
        result = current_app.db.materi.delete_one({
            'title': title,
            'program_title': program_title
        })
        
        if result.deleted_count > 0:
            return jsonify({'msg': 'Materi berhasil dihapus!'})
        else:
            return jsonify({'msg': 'Materi tidak dapat dihapus dari database!'}), 500
    except Exception as e:
        print(f"Error deleting materi: {str(e)}")
        return jsonify({'msg': f'Error: {str(e)}'}), 500

@add_materi_.route('/edit-materi', methods=['POST'])
def edit_materi():
    try:
        # Ensure default cover exists
        ensure_default_cover_exists()
        
        # Get data from form
        title = request.form.get('title')
        program_title = request.form.get('program_title')
        description = request.form.get('description')
        journal = request.form.get('journal')
        
        # Validate required fields
        if not title or not program_title:
            return jsonify({'success': False, 'msg': 'Judul dan program wajib diisi'}), 400
        
        # Create program-specific directories if they don't exist
        program_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'programs', program_title.replace(' ', '_').lower())
        program_img_dir = os.path.join(program_dir, 'img')
        program_pdf_dir = os.path.join(program_dir, 'pdf')
        program_audio_dir = os.path.join(program_dir, 'audio')
        
        for directory in [program_dir, program_img_dir, program_pdf_dir, program_audio_dir]:
            if not os.path.exists(directory):
                os.makedirs(directory)
                print(f"Created directory: {directory}")
        
        # Get existing materi document
        existing_materi = current_app.db.materi.find_one({'title': title, 'program_title': program_title})
        if not existing_materi:
            return jsonify({'success': False, 'msg': 'Materi tidak ditemukan'}), 404
        
        # Initialize update document
        update_doc = {
            'description': description,
            'journal': journal,
            'updated_at': datetime.datetime.now()
        }
        
        # Process cover image
        if 'coverImage' in request.files and request.files['coverImage'].filename:
            try:
                # Delete old cover image if it's not the default
                if existing_materi.get('coverImage') and existing_materi.get('coverImage') != 'default_cover.jpg':
                    old_cover_path = os.path.join(program_img_dir, existing_materi.get('coverImage'))
                    if os.path.exists(old_cover_path):
                        os.remove(old_cover_path)
                        print(f"Deleted old cover image: {old_cover_path}")
                
                # Save new cover image
                cover_file = request.files['coverImage']
                cover_image_filename = secure_filename(f"{title.replace(' ', '_').lower()}_cover{os.path.splitext(cover_file.filename)[1]}")
                cover_file.save(os.path.join(program_img_dir, cover_image_filename))
                update_doc['coverImage'] = f"assets/programs/{program_title.replace(' ', '_').lower()}/img/{cover_image_filename}"
                print(f"Saved new cover image: {cover_image_filename}")
            except Exception as e:
                print(f"Error updating cover image: {str(e)}")
        elif 'existingCoverImage' in request.form:
            # Keep existing cover image
            update_doc['coverImage'] = request.form.get('existingCoverImage')
        
        # Process summary PDF
        if 'summaryPdf' in request.files and request.files['summaryPdf'].filename:
            try:
                # Delete old PDF if it exists
                if existing_materi.get('summary_pdf'):
                    old_pdf_path = os.path.join(current_app.config['STATIC_FOLDER'], existing_materi.get('summary_pdf'))
                    if os.path.exists(old_pdf_path):
                        os.remove(old_pdf_path)
                        print(f"Deleted old PDF: {old_pdf_path}")
                
                # Save new PDF
                pdf_file = request.files['summaryPdf']
                pdf_filename = secure_filename(f"{title.replace(' ', '_').lower()}_summary{os.path.splitext(pdf_file.filename)[1]}")
                pdf_file.save(os.path.join(program_pdf_dir, pdf_filename))
                update_doc['summary_pdf'] = f"assets/programs/{program_title.replace(' ', '_').lower()}/pdf/{pdf_filename}"
                print(f"Saved new PDF: {pdf_filename}")
            except Exception as e:
                print(f"Error updating PDF: {str(e)}")
        elif 'existingSummaryPdf' in request.form:
            # Keep existing PDF
            update_doc['summary_pdf'] = request.form.get('existingSummaryPdf')
        
        # Process relaxation audios
        if 'replaceAudio' in request.form and request.form.get('replaceAudio') == 'true':
            relaxation_audios = []
            
            # Handle individual audio files
            for i in range(1, 3):
                audio_key = f'audioRelaxation{i}'
                keep_key = f'keepExistingAudioRelaxation{i}'
                
                if audio_key in request.files and request.files[audio_key].filename:
                    try:
                        # Delete old audio if it exists
                        if existing_materi.get('relaxation_audios') and len(existing_materi.get('relaxation_audios')) >= i:
                            old_audio_path = os.path.join(current_app.config['STATIC_FOLDER'], existing_materi.get('relaxation_audios')[i-1])
                            if os.path.exists(old_audio_path):
                                os.remove(old_audio_path)
                                print(f"Deleted old relaxation audio {i}: {old_audio_path}")
                        
                        # Save new audio
                        audio_file = request.files[audio_key]
                        audio_filename = secure_filename(f"{title.replace(' ', '_').lower()}_relaxation_{i}{os.path.splitext(audio_file.filename)[1]}")
                        audio_file.save(os.path.join(program_audio_dir, audio_filename))
                        relaxation_audios.append(f"assets/programs/{program_title.replace(' ', '_').lower()}/audio/{audio_filename}")
                        print(f"Saved new relaxation audio {i}: {audio_filename}")
                    except Exception as e:
                        print(f"Error updating relaxation audio {i}: {str(e)}")
                elif keep_key in request.form and request.form.get(keep_key):
                    # Keep existing audio
                    relaxation_audios.append(request.form.get(keep_key))
            
            update_doc['relaxation_audios'] = relaxation_audios
        elif 'keepExistingAudio' in request.form and request.form.get('keepExistingAudio') == 'true':
            # Keep all existing audio files
            if 'existingAudioRelaxation1' in request.form or 'existingAudioRelaxation2' in request.form:
                relaxation_audios = []
                if 'existingAudioRelaxation1' in request.form:
                    relaxation_audios.append(request.form.get('existingAudioRelaxation1'))
                if 'existingAudioRelaxation2' in request.form:
                    relaxation_audios.append(request.form.get('existingAudioRelaxation2'))
                update_doc['relaxation_audios'] = relaxation_audios
            else:
                # Use existing audios from database
                update_doc['relaxation_audios'] = existing_materi.get('relaxation_audios', [])
        
        # Process learning audios
        if 'replaceLearningAudios' in request.form and request.form.get('replaceLearningAudios') == 'true':
            learning_audios = []
            audio_subtitles = []
            
            # Delete all existing learning audios
            if existing_materi.get('learning_audios'):
                for old_audio in existing_materi.get('learning_audios'):
                    old_audio_path = os.path.join(current_app.config['STATIC_FOLDER'], old_audio)
                    if os.path.exists(old_audio_path):
                        os.remove(old_audio_path)
                        print(f"Deleted old learning audio: {old_audio_path}")
            
            # Process new learning audios
            for i in range(9):  # Maximum 9 learning audios
                audio_key = f'learningAudio_{i}'
                subtitle_key = f'audioSubtitle_{i}'
                
                if audio_key in request.files and request.files[audio_key].filename:
                    try:
                        audio_file = request.files[audio_key]
                        audio_filename = secure_filename(f"{title.replace(' ', '_').lower()}_learning_{i}{os.path.splitext(audio_file.filename)[1]}")
                        audio_file.save(os.path.join(program_audio_dir, audio_filename))
                        learning_audios.append(f"assets/programs/{program_title.replace(' ', '_').lower()}/audio/{audio_filename}")
                        
                        # Get corresponding subtitle if available
                        subtitle = request.form.get(subtitle_key, '')
                        audio_subtitles.append(subtitle)
                        print(f"Saved new learning audio {i}: {audio_filename}")
                    except Exception as e:
                        print(f"Error updating learning audio {i}: {str(e)}")
            
            update_doc['learning_audios'] = learning_audios
            update_doc['audio_subtitles'] = audio_subtitles
        elif 'keepExistingLearningAudios' in request.form and request.form.get('keepExistingLearningAudios') == 'true':
            # Keep existing learning audios
            learning_audios = []
            audio_subtitles = []
            
            # Get existing learning audios from form
            i = 0
            while f'existingLearningAudio_{i}' in request.form:
                learning_audios.append(request.form.get(f'existingLearningAudio_{i}'))
                audio_subtitles.append(request.form.get(f'existingAudioSubtitle_{i}', ''))
                i += 1
            
            if learning_audios:
                update_doc['learning_audios'] = learning_audios
                update_doc['audio_subtitles'] = audio_subtitles
            else:
                # Use existing audios from database
                update_doc['learning_audios'] = existing_materi.get('learning_audios', [])
                update_doc['audio_subtitles'] = existing_materi.get('audio_subtitles', [])
        
        # Process illustrations
        if 'replaceIllustrations' in request.form and request.form.get('replaceIllustrations') == 'true':
            illustrations = []
            
            # Delete all existing illustrations
            if existing_materi.get('illustrations'):
                for old_illustration in existing_materi.get('illustrations'):
                    old_illustration_path = os.path.join(current_app.config['STATIC_FOLDER'], old_illustration)
                    if os.path.exists(old_illustration_path):
                        os.remove(old_illustration_path)
                        print(f"Deleted old illustration: {old_illustration_path}")
            
            # Process new illustrations
            for i in range(9):  # Maximum 9 illustrations
                illustration_key = f'illustration_{i}'
                if illustration_key in request.files and request.files[illustration_key].filename:
                    try:
                        illustration_file = request.files[illustration_key]
                        illustration_filename = secure_filename(f"{title.replace(' ', '_').lower()}_illustration_{i}{os.path.splitext(illustration_file.filename)[1]}")
                        illustration_file.save(os.path.join(program_img_dir, illustration_filename))
                        illustrations.append(f"assets/programs/{program_title.replace(' ', '_').lower()}/img/{illustration_filename}")
                        print(f"Saved new illustration {i}: {illustration_filename}")
                    except Exception as e:
                        print(f"Error updating illustration {i}: {str(e)}")
            
            update_doc['illustrations'] = illustrations
        elif 'keepExistingIllustrations' in request.form and request.form.get('keepExistingIllustrations') == 'true':
            # Keep existing illustrations
            illustrations = []
            
            # Get existing illustrations from form
            i = 0
            while f'existingIllustration_{i}' in request.form:
                illustrations.append(request.form.get(f'existingIllustration_{i}'))
                i += 1
            
            if illustrations:
                update_doc['illustrations'] = illustrations
            else:
                # Use existing illustrations from database
                update_doc['illustrations'] = existing_materi.get('illustrations', [])
        
        # Update MongoDB document
        result = current_app.db.materi.update_one(
            {'title': title, 'program_title': program_title},
            {'$set': update_doc}
        )
        
        if result.modified_count > 0 or result.matched_count > 0:
            return jsonify({'success': True, 'msg': 'Materi berhasil diperbarui'})
        else:
            return jsonify({'success': False, 'msg': 'Tidak ada perubahan yang disimpan'}), 400
    except Exception as e:
        print(f"Error in edit_materi: {str(e)}")
        return jsonify({'success': False, 'msg': f'Terjadi kesalahan: {str(e)}'}), 500

@add_materi_.route('/detail-materi/<sesi>')
def detail_materi(sesi):
    # First try to find by title
    materi = current_app.db.materi.find_one({'title': sesi}, {'_id': False})
    
    # If not found, try with sesi field as fallback
    if materi is None:
        materi = current_app.db.materi.find_one({'sesi': sesi}, {'_id': False})
    
    if materi is None:
        return jsonify({'msg': 'Materi tidak ditemukan!'}), 404
    
    return jsonify({'msg': 'Materi berhasil ditemukan!', 'materi': materi})

@add_materi_.route('/add-materi/<program_title>')
def view_program_materi(program_title):
    myToken = request.cookies.get("mytoken")
    SECRET_KEY = current_app.config['SECRET_KEY']
    try:
        payload = jwt.decode(myToken, SECRET_KEY, algorithms=["HS256"])
        user_info = current_app.db.users_admin.find_one({"username": payload["id"]})

        if user_info and user_info.get('username') == 'admin.psidamai':
            return render_template('dashboard_admin/add_materi.html', 
                                user_info=user_info, 
                                program_title=program_title)
        else:
            return redirect(url_for("auth_admin.login_admin"))
        
    except jwt.ExpiredSignatureError:
        return redirect(url_for("auth_admin.login_admin"))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("auth_admin.login_admin"))

def check_file_exists(file_path):
    """Memeriksa apakah file ada di sistem file"""
    if not file_path or not file_path.startswith('/static/'):
        return False
    
    # Konversi path dari /static/... ke path sistem file yang sebenarnya
    real_path = os.path.join(current_app.root_path, file_path[1:])
    exists = os.path.exists(real_path)
    print(f"Checking file: {real_path} - Exists: {exists}")
    return exists

def ensure_directories_exist():
    """Memastikan semua direktori yang diperlukan ada"""
    # Direktori untuk gambar materi
    materi_img_dir = os.path.join(current_app.root_path, "static", "assets", "img", "materi")
    if not os.path.exists(materi_img_dir):
        os.makedirs(materi_img_dir, exist_ok=True)
        print(f"Created directory: {materi_img_dir}")
    
    # Direktori untuk program
    programs_dir = os.path.join(current_app.root_path, "static", "assets", "programs")
    if not os.path.exists(programs_dir):
        os.makedirs(programs_dir, exist_ok=True)
        print(f"Created directory: {programs_dir}")
    
    # Direktori untuk PDF
    pdf_dir = os.path.join(current_app.root_path, "static", "assets", "pdf")
    if not os.path.exists(pdf_dir):
        os.makedirs(pdf_dir, exist_ok=True)
        print(f"Created directory: {pdf_dir}")
    
    # Direktori untuk audio
    audio_dir = os.path.join(current_app.root_path, "static", "assets", "audio")
    if not os.path.exists(audio_dir):
        os.makedirs(audio_dir, exist_ok=True)
        print(f"Created directory: {audio_dir}")
    
    # Pastikan UPLOAD_FOLDER ada dalam konfigurasi
    if not hasattr(current_app.config, 'UPLOAD_FOLDER') or not current_app.config.get('UPLOAD_FOLDER'):
        current_app.config['UPLOAD_FOLDER'] = os.path.join(current_app.root_path, 'static', 'assets')
        print(f"UPLOAD_FOLDER not found in config, using: {current_app.config['UPLOAD_FOLDER']}")
    
    # Pastikan STATIC_FOLDER ada dalam konfigurasi
    if not hasattr(current_app.config, 'STATIC_FOLDER') or not current_app.config.get('STATIC_FOLDER'):
        current_app.config['STATIC_FOLDER'] = os.path.join(current_app.root_path, 'static')
        print(f"STATIC_FOLDER not found in config, using: {current_app.config['STATIC_FOLDER']}")
    
    # Pastikan direktori static ada
    static_dir = os.path.join(current_app.root_path, "static")
    if not os.path.exists(static_dir):
        os.makedirs(static_dir, exist_ok=True)
        print(f"Created directory: {static_dir}")
    
    # Pastikan direktori assets ada
    assets_dir = os.path.join(current_app.root_path, "static", "assets")
    if not os.path.exists(assets_dir):
        os.makedirs(assets_dir, exist_ok=True)
        print(f"Created directory: {assets_dir}")
    
    # Pastikan direktori temp ada
    temp_dir = os.path.join(current_app.root_path, "temp")
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir, exist_ok=True)
        print(f"Created directory: {temp_dir}")
    
    print("All required directories checked and created if needed.")

@add_materi_.route('/materi-details/<program_title>/<materi_title>', methods=['GET'])
def materi_details(program_title, materi_title):
    myToken = request.cookies.get("mytoken")
    SECRET_KEY = current_app.config['SECRET_KEY']
    try:
        payload = jwt.decode(myToken, SECRET_KEY, algorithms=["HS256"])
        user_info = current_app.db.users_admin.find_one({"username": payload["id"]})

        if user_info and user_info.get('username') == 'admin.psidamai':
            # Pastikan direktori yang diperlukan ada
            ensure_directories_exist()
            ensure_default_cover_exists()
            
            # Ambil data materi dari database
            materi = current_app.db.materi.find_one({
                'program_title': program_title,
                'title': materi_title
            })
            
            if not materi:
                print(f"Materi tidak ditemukan: {program_title}/{materi_title}")
                return redirect(url_for('add_materi.view_program_materi', program_title=program_title))
            
            print(f"Materi ditemukan: {materi}")
            
            # Siapkan data untuk template
            cover_image_path = None
            if materi.get('coverImage'):
                if materi['coverImage'] == 'default_cover.jpg':
                    cover_image_path = '/static/assets/img/materi/default_cover.jpg'
                    print(f"Menggunakan cover default: {cover_image_path}")
                else:
                    cover_image_path = f"/static/{materi['coverImage']}"
                    print(f"Menggunakan cover dari database: {cover_image_path}")
                    
                    # Periksa apakah file ada
                    if not check_file_exists(cover_image_path):
                        print(f"Cover image tidak ditemukan: {cover_image_path}")
                        cover_image_path = '/static/assets/img/materi/default_cover.jpg'
            else:
                cover_image_path = '/static/assets/img/materi/default_cover.jpg'
                print(f"Tidak ada cover, menggunakan default: {cover_image_path}")
            
            # Siapkan path PDF
            pdf_path = None
            if materi.get('summary_pdf'):
                pdf_path = f"/static/{materi['summary_pdf']}"
                print(f"PDF path: {pdf_path}")
                
                # Periksa apakah file ada
                if not check_file_exists(pdf_path):
                    print(f"PDF tidak ditemukan: {pdf_path}")
                    pdf_path = None
            
            # Siapkan data audio pembelajaran dengan subtitle
            learning_audio_data = []
            if materi.get('learning_audios'):
                for i, audio_path in enumerate(materi['learning_audios']):
                    full_path = f"/static/{audio_path}"
                    
                    # Periksa apakah file ada
                    if check_file_exists(full_path):
                        audio_data = {
                            'path': full_path,
                            'filename': os.path.basename(audio_path),
                            'subtitle': materi.get('audio_subtitles', [])[i] if i < len(materi.get('audio_subtitles', [])) else ''
                        }
                        learning_audio_data.append(audio_data)
                    else:
                        print(f"Audio pembelajaran tidak ditemukan: {full_path}")
                
                print(f"Learning audio data: {learning_audio_data}")
            
            # Siapkan path audio relaksasi
            relaxation_audio_paths = []
            if materi.get('relaxation_audios'):
                for audio_path in materi['relaxation_audios']:
                    full_path = f"/static/{audio_path}"
                    
                    # Periksa apakah file ada
                    if check_file_exists(full_path):
                        relaxation_audio_paths.append(full_path)
                    else:
                        print(f"Audio relaksasi tidak ditemukan: {full_path}")
                
                print(f"Relaxation audio paths: {relaxation_audio_paths}")
            
            # Siapkan path ilustrasi
            illustration_paths = []
            if materi.get('illustrations'):
                for img_path in materi['illustrations']:
                    full_path = f"/static/{img_path}"
                    
                    # Periksa apakah file ada
                    if check_file_exists(full_path):
                        illustration_paths.append(full_path)
                    else:
                        print(f"Ilustrasi tidak ditemukan: {full_path}")
                
                print(f"Illustration paths: {illustration_paths}")
            
            return render_template('dashboard_admin/materi_details.html', 
                                  materi=materi,
                                  program_title=program_title,
                                  cover_image_path=cover_image_path,
                                  pdf_path=pdf_path,
                                  learning_audio_data=learning_audio_data,
                                  relaxation_audio_paths=relaxation_audio_paths,
                                  illustration_paths=illustration_paths)
        else:
            return redirect(url_for('auth_admin.login_admin'))
    except Exception as e:
        print(f"Error in materi_details: {str(e)}")
        return redirect(url_for('auth_admin.login_admin'))

def format_timestamp(seconds):
    """Convert seconds to SRT timestamp format"""
    td = timedelta(seconds=seconds)
    hours = td.seconds//3600
    minutes = (td.seconds//60)%60
    seconds = td.seconds%60
    milliseconds = td.microseconds//1000
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"

def create_word_level_subtitles(text, duration):
    """Create word-level subtitles with estimated timing"""
    # Split text into sentences
    import re
    sentences = re.split(r'(?<=[.!?])\s+', text)
    
    # Remove empty sentences
    sentences = [s.strip() for s in sentences if s.strip()]
    
    if not sentences:
        # If no sentences found, treat the whole text as one sentence
        sentences = [text]
    
    total_chars = sum(len(s) for s in sentences)
    
    # Distribute time based on sentence length
    subtitles = []
    current_time = 0
    
    for sentence in sentences:
        # Calculate sentence duration based on its proportion of the total text
        sentence_duration = (len(sentence) / total_chars) * duration if total_chars > 0 else duration / len(sentences)
        
        # Minimum duration of 1 second per sentence
        sentence_duration = max(sentence_duration, 1.0)
        
        # Add subtitle entry
        subtitles.append({
            'start': current_time,
            'end': current_time + sentence_duration,
            'text': sentence
        })
        
        current_time += sentence_duration
    
    # Adjust the last subtitle to match the total duration
    if subtitles and duration > 0:
        subtitles[-1]['end'] = duration
    
    return subtitles

def convert_audio_to_wav(input_file, output_file):
    """Konversi file audio ke format WAV menggunakan pydub"""
    try:
        print(f"Converting {input_file} to {output_file}")
        print(f"Using FFmpeg at: {FFMPEG_EXE}")
        
        if not os.path.exists(FFMPEG_EXE):
            print(f"FFmpeg not found at: {FFMPEG_EXE}")
            return False
            
        # Try direct FFmpeg command for more control
        try:
            # Create command with explicit parameters
            cmd = [
                FFMPEG_EXE,
                "-y",  # Overwrite output file if it exists
                "-i", input_file,  # Input file
                "-acodec", "pcm_s16le",  # Audio codec
                "-ac", "1",  # Mono
                "-ar", "16000",  # Sample rate
                output_file  # Output file
            ]
            
            print(f"Running FFmpeg command: {' '.join(cmd)}")
            
            # Run the command
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            stdout, stderr = process.communicate()
            
            # Check if conversion was successful
            if process.returncode == 0 and os.path.exists(output_file):
                print(f"Successfully converted to {output_file} using direct FFmpeg command")
                return True
            else:
                print(f"FFmpeg direct command failed with return code {process.returncode}")
                print(f"FFmpeg stderr: {stderr.decode('utf-8', errors='ignore')}")
                # Fall back to pydub method
                print("Falling back to pydub method")
        except Exception as e:
            print(f"Error with direct FFmpeg command: {str(e)}")
            print("Falling back to pydub method")
            
        # Fallback: Use pydub method
        # Load file audio
        audio = AudioSegment.from_file(input_file)
        
        # Konversi ke mono dan set sample rate
        audio = audio.set_channels(1)
        audio = audio.set_frame_rate(16000)
        
        # Export ke WAV dengan parameter yang lebih spesifik
        audio.export(
            output_file,
            format='wav',
            parameters=[
                "-ac", "1",  # mono
                "-ar", "16000",  # sample rate
                "-acodec", "pcm_s16le"  # codec
            ]
        )
        
        if os.path.exists(output_file):
            print(f"Successfully converted to {output_file}")
            return True
        else:
            print(f"Output file {output_file} was not created")
            return False
            
    except Exception as e:
        print(f"Conversion error: {str(e)}")
        return False

def get_audio_duration(audio_path):
    """Get duration of audio file in seconds"""
    try:
        if not os.path.exists(FFPROBE_EXE):
            print(f"FFprobe not found at: {FFPROBE_EXE}")
            return 0
            
        audio = AudioSegment.from_wav(audio_path)
        return len(audio) / 1000.0  # Convert to seconds
    except Exception as e:
        print(f"Error getting duration: {str(e)}")
        return 0

@add_materi_.route('/convert-audio-to-text', methods=['POST'])
def convert_audio_to_text():
    if 'audio' not in request.files:
        return jsonify({'success': False, 'error': 'File audio tidak ditemukan'}), 400
        
    audio_file = request.files['audio']
    
    if not audio_file.filename:
        return jsonify({'success': False, 'error': 'Tidak ada file yang dipilih'}), 400

    # Buat direktori temporary jika belum ada
    temp_dir = os.path.join(current_app.root_path, 'temp')
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    
    # Generate unique filenames to avoid conflicts
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    input_path = os.path.join(temp_dir, f"{timestamp}_{secure_filename(audio_file.filename)}")
    output_path = os.path.join(temp_dir, f"{timestamp}_output.wav")
    
    try:
        # Simpan file audio original
        print(f"Saving audio file to: {input_path}")
        audio_file.save(input_path)
        
        if not os.path.exists(input_path):
            return jsonify({'success': False, 'error': 'Gagal menyimpan file audio'}), 400
            
        print(f"File saved successfully. Size: {os.path.getsize(input_path)} bytes")
        
        # Konversi audio ke WAV
        if not convert_audio_to_wav(input_path, output_path):
            return jsonify({
                'success': False, 
                'error': 'Gagal mengkonversi file audio ke format WAV. Pastikan file audio valid dan format didukung (mp3, wav, ogg, m4a).'
            }), 400
            
        if not os.path.exists(output_path):
            return jsonify({'success': False, 'error': 'File WAV tidak berhasil dibuat'}), 400
            
        print(f"WAV file created successfully. Size: {os.path.getsize(output_path)} bytes")
        
        # Get audio duration
        duration = get_audio_duration(output_path)
        print(f"Audio duration: {duration} seconds")
        
        # Inisialisasi recognizer
        recognizer = Recognizer()
        
        with AudioFile(output_path) as source:
            print("Reading audio file with recognizer")
            # Sesuaikan dengan noise lingkungan
            recognizer.adjust_for_ambient_noise(source)
            # Rekam audio
            audio_data = recognizer.record(source)
            
            try:
                # Gunakan Bahasa Indonesia
                print("Starting speech recognition...")
                text = recognizer.recognize_google(audio_data, language='id-ID')
                print(f"Speech recognition completed. Text length: {len(text)}")
                
                # Jika tidak ada teks yang dikenali
                if not text or len(text.strip()) == 0:
                    return jsonify({
                        'success': False,
                        'error': 'Tidak ada teks yang dapat dikenali dalam audio tersebut'
                    }), 400
                
                # Buat subtitle per kata dengan timing
                subtitles = create_word_level_subtitles(text, duration)
                
                # Format konten SRT
                srt_content = ''
                for i, sub in enumerate(subtitles, 1):
                    start_time = format_timestamp(sub['start'])
                    end_time = format_timestamp(sub['end'])
                    srt_content += f"{i}\n"
                    srt_content += f"{start_time} --> {end_time}\n"
                    srt_content += f"{sub['text']}\n\n"
                
                return jsonify({
                    'success': True,
                    'text': text,
                    'subtitles': srt_content,
                    'subtitle_entries': subtitles
                })
                
            except UnknownValueError:
                return jsonify({
                    'success': False, 
                    'error': 'Tidak dapat memahami audio tersebut. Pastikan audio berisi suara yang jelas dan tidak terlalu banyak noise.'
                }), 400
            except RequestError as e:
                return jsonify({
                    'success': False, 
                    'error': f'Terjadi kesalahan pada layanan pengenalan suara: {str(e)}'
                }), 500
            
    except Exception as e:
        print(f"General error: {str(e)}")
        return jsonify({
            'success': False, 
            'error': f'Terjadi kesalahan: {str(e)}'
        }), 500
        
    finally:
        # Bersihkan file temporary
        try:
            if os.path.exists(input_path):
                os.remove(input_path)
            if os.path.exists(output_path):
                os.remove(output_path)
        except Exception as e:
            print(f"Error cleaning up temporary files: {str(e)}")

# Function to ensure default cover image exists
def ensure_default_cover_exists():
    default_cover_path = os.path.join(current_app.root_path, "static", "assets", "img", "materi", "default_cover.jpg")
    if not os.path.exists(default_cover_path):
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(default_cover_path), exist_ok=True)
        
        # Create a simple default image or copy from a template
        try:
            # Option 1: Copy from a template if it exists
            template_path = os.path.join(current_app.root_path, "static", "assets", "img", "default_cover.jpg")
            if os.path.exists(template_path):
                shutil.copy(template_path, default_cover_path)
                print(f"Created default cover image by copying from template")
            elif PIL_AVAILABLE:
                # Option 2: Create a simple image with PIL
                create_default_image(default_cover_path)
                print(f"Created default cover image with PIL")
            else:
                # Option 3: Create a simple text file as placeholder (not ideal but better than nothing)
                with open(default_cover_path, 'w') as f:
                    f.write("Default cover image placeholder")
                print(f"Created default cover image placeholder")
        except Exception as e:
            print(f"Warning: Could not create default cover image: {str(e)}")

def create_default_image(path, width=800, height=400):
    """Create a simple default image using PIL"""
    if not PIL_AVAILABLE:
        return False
    
    try:
        # Create a new image with white background
        image = Image.new('RGB', (width, height), color=(240, 240, 240))
        draw = ImageDraw.Draw(image)
        
        # Draw a border
        border_width = 10
        draw.rectangle(
            [(border_width, border_width), (width - border_width, height - border_width)],
            outline=(200, 200, 200),
            width=border_width
        )
        
        # Draw text
        try:
            # Try to use a font if available
            font = ImageFont.truetype("arial.ttf", 72)
        except IOError:
            # Use default font if arial is not available
            font = ImageFont.load_default()
        
        text = "No Image"
        text_width = draw.textlength(text, font=font) if hasattr(draw, 'textlength') else font.getsize(text)[0]
        text_position = ((width - text_width) / 2, height / 2 - 36)
        draw.text(text_position, text, fill=(100, 100, 100), font=font)
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        # Save the image
        image.save(path, 'JPEG', quality=90)
        print(f"Default image created at: {path}")
        return True
    except Exception as e:
        print(f"Error creating default image: {str(e)}")
        return False

@add_materi_.route('/test-audio-conversion')
def test_audio_conversion():
    """Test route to check if audio conversion works"""
    try:
        # Print environment information
        print(f"FFmpeg path: {FFMPEG_PATH}")
        print(f"FFmpeg executable: {FFMPEG_EXE}")
        print(f"FFprobe executable: {FFPROBE_EXE}")
        print(f"FFmpeg exists: {os.path.exists(FFMPEG_EXE)}")
        print(f"FFprobe exists: {os.path.exists(FFPROBE_EXE)}")
        
        # Check if pydub is configured correctly
        print(f"Pydub converter: {AudioSegment.converter}")
        print(f"Pydub ffmpeg: {AudioSegment.ffmpeg}")
        print(f"Pydub ffprobe: {AudioSegment.ffprobe}")
        
        # Create test directories
        temp_dir = os.path.join(current_app.root_path, 'temp')
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
        
        # Try to create a simple audio file
        try:
            from pydub.generators import Sine
            
            # Generate a simple sine wave
            sine_wave = Sine(440).to_audio_segment(duration=1000)  # 1 second 440 Hz sine wave
            
            # Save as MP3
            mp3_path = os.path.join(temp_dir, 'test.mp3')
            sine_wave.export(mp3_path, format="mp3")
            
            # Try to convert to WAV
            wav_path = os.path.join(temp_dir, 'test.wav')
            result = convert_audio_to_wav(mp3_path, wav_path)
            
            # Check results
            conversion_success = result and os.path.exists(wav_path)
            
            # Clean up
            if os.path.exists(mp3_path):
                os.remove(mp3_path)
            if os.path.exists(wav_path):
                os.remove(wav_path)
            
            return jsonify({
                'success': True,
                'conversion_success': conversion_success,
                'ffmpeg_path': FFMPEG_EXE,
                'ffmpeg_exists': os.path.exists(FFMPEG_EXE),
                'message': 'Audio conversion test completed'
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Error generating test audio: {str(e)}',
                'ffmpeg_path': FFMPEG_EXE,
                'ffmpeg_exists': os.path.exists(FFMPEG_EXE)
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'General error: {str(e)}'
        })
