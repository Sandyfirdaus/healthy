from flask import Flask, redirect, current_app, jsonify, url_for, render_template, Blueprint, request
import jwt
from datetime import datetime
from urllib.parse import unquote

program_details_ = Blueprint('program_details', __name__)

@program_details_.route("/materi/<path:program_title>/<path:materi_title>")
def materi_details(program_title, materi_title):
    # URL decode the titles since they may contain spaces and special characters
    program_title = unquote(program_title)
    materi_title = unquote(materi_title)
    
    myToken = request.cookies.get("mytoken")
    SECRET_KEY = current_app.config['SECRET_KEY']
    try:
        payload = jwt.decode(myToken, SECRET_KEY, algorithms=["HS256"])
        user_info = current_app.db.users.find_one({"username": payload["id"]})
        
        # Fetch the specific materi from database
        materi = current_app.db.materi.find_one({
            "program_title": program_title,
            "title": materi_title
        }, {'_id': False})
        
        if not materi:
            return redirect(url_for('program_content.program_content', program_title=program_title))
            
        # Format materi data for template
        materi_data = {
            'judul': materi['title'],
            'deskripsi': materi.get('description', ''),
            'naskah': materi.get('summary_pdf', ''),
            'ilustrasi': [],
            'audio': [],
            'audio_pembelajaran': [],
            'program_title': program_title
        }

        # Add illustrations
        if materi.get('illustrations'):
            materi_data['ilustrasi'] = materi['illustrations']

        # Add relaxation audios if available
        if materi.get('relaxation_audios'):
            for i, audio_path in enumerate(materi['relaxation_audios']):
                materi_data['audio'].append({
                    'judul': f"Audio Relaksasi {i+1}",
                    'src': audio_path
                })

        # Process learning audios with their subtitles
        if materi.get('learning_audios'):
            for i, audio_path in enumerate(materi['learning_audios']):
                audio_item = {
                    'src': audio_path,
                    'image': materi.get('illustrations', [])[i] if i < len(materi.get('illustrations', [])) else None,
                    'transkrip': [],
                    'judul': f"Audio Pembelajaran {i+1}"
                }
                
                # Add subtitle if available
                if materi.get('audio_subtitles') and i < len(materi['audio_subtitles']):
                    subtitle_text = materi['audio_subtitles'][i]
                    if subtitle_text:
                        try:
                            # Convert plain text to SRT format if it's not already in SRT format
                            if not is_srt_format(subtitle_text):
                                subtitle_text = convert_to_srt_format(subtitle_text)
                            
                            # Parse SRT format subtitles
                            lines = subtitle_text.strip().split('\n\n')
                            current_time = 0
                            
                            for line in lines:
                                parts = line.strip().split('\n')
                                if len(parts) >= 3:  # Valid subtitle entry
                                    try:
                                        # Parse timecode (00:00:00,000 --> 00:00:00,000)
                                        times = parts[1].split(' --> ')
                                        start_time = parse_timecode(times[0].strip())
                                        end_time = parse_timecode(times[1].strip())
                                        
                                        # Add to transcript list
                                        audio_item['transkrip'].append({
                                            'start': start_time,
                                            'end': end_time,
                                            'text': parts[2]
                                        })
                                    except Exception as e:
                                        print(f"Error parsing subtitle entry: {e}")
                                        continue
                            
                            # Sort transcripts by start time
                            audio_item['transkrip'].sort(key=lambda x: x['start'])
                            
                        except Exception as e:
                            print(f"Error processing subtitles: {e}")
                
                materi_data['audio_pembelajaran'].append(audio_item)

        print("Debug - Formatted materi_data:", materi_data)  # Debug print
        
        return render_template('dashboard/materi_details.html', 
                            materi=materi_data,
                            user_info=user_info)
                            
    except jwt.ExpiredSignatureError:
        return redirect(url_for("auth.login"))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("auth.login"))

@program_details_.route('/save-status', methods=["POST"])
def save_status():
    try:
        username = request.form['username']
        materi_title = request.form['materi']
        program_title = request.form.get('program_title', '')
        status = request.form['status']
        
        # Get current date and time
        now = datetime.now()
        tanggal = now.strftime("%Y-%m-%d")
        waktu = now.strftime("%H:%M:%S")
        
        # Get materi details from database to get the correct program
        materi_info = current_app.db.materi.find_one({"title": materi_title})
        if materi_info:
            program_title = materi_info.get('program_title', program_title)
        
        # Check if status already exists in status_materi collection
        exists = bool(current_app.db.status_materi.find_one({"username": username, "materi": materi_title}))
        
        if exists:
            return jsonify({
                "exists": exists,
                "msg": "Status materi sudah tersimpan"
            })
        else:
            # Save to status_materi collection with complete information
            status_doc = {
                "username": username,
                "program": program_title,  # Using the program title from materi database
                "materi": materi_title,
                "status": "Completed",
                "tanggal": tanggal,
                "waktu": waktu,
                "timestamp": now
            }
            current_app.db.status_materi.insert_one(status_doc)
            
            return jsonify({
                "exists": exists,
                "msg": "Status materi berhasil disimpan"
            })
    except Exception as e:
        print("Error saving status:", str(e))
        return jsonify({
            "result": "Error",
            "message": "Gagal menyimpan status materi"
        }), 500

@program_details_.route('/check-status', methods=["GET"])
def check_status():
    try:
        myToken = request.cookies.get("mytoken")
        SECRET_KEY = current_app.config['SECRET_KEY']
        payload = jwt.decode(myToken, SECRET_KEY, algorithms=["HS256"])
        username = payload["id"]
        
        progres = list(current_app.db.status_materi.find({"username": username}, {'_id': False}))
        return jsonify({"progres": progres})
    except Exception as e:
        print("Error checking status:", str(e))
        return jsonify({
            "result": "Error",
            "message": "Gagal mengecek status materi"
        }), 500

def is_srt_format(text):
    """Check if the text is already in SRT format"""
    lines = text.strip().split('\n')
    if len(lines) < 4:  # SRT needs at least 4 lines for one entry
        return False
    
    try:
        # Check first line is a number
        int(lines[0])
        # Check second line contains ' --> '
        return ' --> ' in lines[1]
    except:
        return False

def convert_to_srt_format(text):
    """Convert plain text to SRT format with estimated timings"""
    # Split text into sentences
    import re
    sentences = re.split(r'[.!?]+\s*', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    def format_timecode(seconds):
        """Convert seconds to SRT timecode format"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds_part = seconds % 60
        milliseconds = int((seconds_part % 1) * 1000)
        seconds_whole = int(seconds_part)
        return f"{hours:02d}:{minutes:02d}:{seconds_whole:02d},{milliseconds:03d}"
    
    # Generate SRT format with continuous timing
    srt_parts = []
    current_time = 0.0
    
    for i, sentence in enumerate(sentences, 1):
        # Calculate duration based on sentence length
        # Minimum 3 seconds, plus additional time based on word count
        words = len(sentence.split())
        duration = max(3.0, words * 0.5)  # 0.5 seconds per word
        
        start_time = current_time
        end_time = start_time + duration
        
        # Format the subtitle entry
        srt_parts.append(
            f"{i}\n"
            f"{format_timecode(start_time)} --> {format_timecode(end_time)}\n"
            f"{sentence}\n"
        )
        
        # Update current_time for next subtitle
        current_time = end_time
    
    return "\n".join(srt_parts)

def parse_timecode(timecode):
    """Convert SRT timecode to seconds"""
    try:
        # Split timecode into parts (00:00:00,000)
        time_parts = timecode.replace(',', '.').split(':')
        hours = int(time_parts[0])
        minutes = int(time_parts[1])
        seconds = float(time_parts[2])
        
        # Convert to total seconds
        return hours * 3600 + minutes * 60 + seconds
    except Exception as e:
        print(f"Error parsing timecode {timecode}: {e}")
        return 0.0