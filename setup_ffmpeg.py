import os
import sys
import requests
import zipfile
from io import BytesIO
import shutil
import platform

def download_ffmpeg():
    # Create directory if it doesn't exist
    ffmpeg_dir = os.path.join("app", "utils", "ffmpeg")
    os.makedirs(ffmpeg_dir, exist_ok=True)
    
    # Determine the correct download URL based on the operating system
    system = platform.system().lower()
    if system == "windows":
        # Windows - download from BtbN's builds
        ffmpeg_url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
    elif system == "darwin":
        # macOS
        print("For macOS, please install FFmpeg using Homebrew: brew install ffmpeg")
        print("Then create symbolic links in the app/utils/ffmpeg directory")
        return
    elif system == "linux":
        # Linux
        print("For Linux, please install FFmpeg using your package manager.")
        print("For example: sudo apt-get install ffmpeg")
        print("Then create symbolic links in the app/utils/ffmpeg directory")
        return
    else:
        print(f"Unsupported operating system: {system}")
        return
    
    # Download the file
    print(f"Downloading FFmpeg from {ffmpeg_url}...")
    try:
        response = requests.get(ffmpeg_url, stream=True)
        response.raise_for_status()  # Raise an exception for HTTP errors
        
        # Save the zip file
        zip_path = os.path.join("app", "utils", "ffmpeg.zip")
        with open(zip_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        # Extract the zip file
        print("Extracting FFmpeg...")
        with zipfile.ZipFile(zip_path) as zip_ref:
            # Create a temporary directory for extraction
            temp_dir = os.path.join("app", "utils", "temp_ffmpeg")
            os.makedirs(temp_dir, exist_ok=True)
            zip_ref.extractall(temp_dir)
            
            # Find the bin directory containing the executables
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    if file.endswith(".exe") and (file == "ffmpeg.exe" or file == "ffprobe.exe" or file == "ffplay.exe"):
                        # Copy the executable to the ffmpeg directory
                        src_path = os.path.join(root, file)
                        dst_path = os.path.join(ffmpeg_dir, file)
                        shutil.copy2(src_path, dst_path)
                        print(f"Copied {file} to {ffmpeg_dir}")
        
        # Clean up
        print("Cleaning up...")
        if os.path.exists(zip_path):
            os.remove(zip_path)
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        
        print("FFmpeg setup completed successfully!")
        
    except Exception as e:
        print(f"Error downloading or extracting FFmpeg: {e}")
        print("Please download FFmpeg manually from https://ffmpeg.org/download.html")
        print("and place the executables in the app/utils/ffmpeg directory.")

if __name__ == "__main__":
    download_ffmpeg() 