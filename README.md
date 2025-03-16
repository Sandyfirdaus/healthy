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

## Deployment to Railway

This application is configured to deploy smoothly on Railway. The code has been updated to handle the absence of local FFmpeg executables by using the system-installed FFmpeg on Railway.

### Railway Deployment Steps

1. Push your code to a GitHub repository
2. Connect your repository to Railway
3. Railway will automatically detect the configuration in `railway.toml` and install FFmpeg during deployment
4. The application will use the system-installed FFmpeg on Railway

### Alternative: Docker Deployment

You can also deploy using the provided Dockerfile:

1. Build the Docker image:
   ```
   docker build -t psidamai-app .
   ```
2. Run the container:
   ```
   docker run -p 5000:5000 psidamai-app
   ```

## GitHub Large File Handling
The FFmpeg executables are excluded from the repository using `.gitignore` because they exceed GitHub's recommended file size limits. This approach ensures:

1. Faster cloning and pulling of the repository
2. No issues with GitHub's file size limitations
3. Better repository management 