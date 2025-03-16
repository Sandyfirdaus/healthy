# PSIDAMAI Mental Health Application

## Setup Instructions

### FFmpeg Setup
This application requires FFmpeg for audio/video processing. The FFmpeg executables are not included in the repository due to their large size (>80MB each).

#### Option 1: Automatic Setup (Recommended)
Run the provided setup script to automatically download and set up FFmpeg:
```
python setup_ffmpeg.py
```

#### Option 2: Manual Setup
If the automatic setup doesn't work, you can download FFmpeg manually:

1. Go to https://ffmpeg.org/download.html or https://github.com/BtbN/FFmpeg-Builds/releases
2. Download the appropriate version for your operating system
3. Extract the downloaded archive
4. Copy the following files to the `app/utils/ffmpeg` directory:
   - ffmpeg.exe
   - ffprobe.exe
   - ffplay.exe

### Installation
1. Clone this repository
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Set up FFmpeg as described above
4. Run the application:
   ```
   python app.py
   ```

## GitHub Large File Handling
The FFmpeg executables are excluded from the repository using `.gitignore` because they exceed GitHub's recommended file size limits. This approach ensures:

1. Faster cloning and pulling of the repository
2. No issues with GitHub's file size limitations
3. Better repository management 