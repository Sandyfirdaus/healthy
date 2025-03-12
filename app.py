from app import create_app
import os

# Konfigurasi path ffmpeg
FFMPEG_PATH = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'utils', 'ffmpeg'))
FFMPEG_EXE = os.path.join(FFMPEG_PATH, 'ffmpeg.exe')
FFPROBE_EXE = os.path.join(FFMPEG_PATH, 'ffprobe.exe')

app = create_app()

if __name__ == '__main__':
    app.run('0.0.0.0',port=5000,debug=True)