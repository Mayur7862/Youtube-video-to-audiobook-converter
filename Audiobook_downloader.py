import os
import sys
import subprocess
from pydub import AudioSegment
import yt_dlp as youtube_dl

# Check if ffmpeg is installed
def check_ffmpeg():
    try:
        subprocess.check_output(['ffmpeg', '-version'], stderr=subprocess.STDOUT)
        print("FFmpeg is installed.")
    except subprocess.CalledProcessError:
        print("FFmpeg is not installed or not found in PATH. Please install FFmpeg.")
        sys.exit(1)

# Download video as audio
def download_audio_from_youtube(url, output_file):
    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': output_file,
            'postprocessors': [{
                'key': 'FFmpegAudioConvertor',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            print("Downloading audio...")
            ydl.download([url])
            print(f"Download complete: {output_file}")
    except Exception as e:
        print(f"Error during downloading: {e}")
        sys.exit(1)

# Convert timestamp string (e.g., "00:00:10") to seconds
def timestamp_to_seconds(timestamp):
    hours, minutes, seconds = map(int, timestamp.split(":"))
    return hours * 3600 + minutes * 60 + seconds

# Read timestamps and names from file
def read_timestamps_from_file(file_path):
    try:
        with open(file_path, 'r') as file:
            timestamps_with_names = []
            for line in file:
                # Split each line into timestamp and name
                parts = line.strip().split(" ", 1)
                if len(parts) == 2:
                    timestamps_with_names.append((parts[0], parts[1]))
            return timestamps_with_names
    except Exception as e:
        print(f"Error reading the timestamps file: {e}")
        sys.exit(1)

# Split the audio based on timestamps and book/chapter names
def split_audio_by_timestamps_and_names(audio_file, timestamps_with_names, output_dir):
    try:
        print("Loading audio...")
        audio = AudioSegment.from_mp3(audio_file)

        for idx, (timestamp, name) in enumerate(timestamps_with_names):
            start_time = timestamp_to_seconds(timestamp) * 1000  # convert to milliseconds
            # Determine the end time by subtracting 1 second from the next timestamp, or use the end of the file for the last segment
            if idx + 1 < len(timestamps_with_names):
                end_time = timestamp_to_seconds(timestamps_with_names[idx + 1][0]) * 1000 - 1000  # subtract 1 second from next timestamp
            else:
                end_time = len(audio)  # set end time to the end of the audio for the last part
            
            # Create a valid file name for the output based on the name
            output_file = os.path.join(output_dir, f"{name.replace(' ', '_').replace(':', '')}.mp3")
            print(f"Processing: {name}... Start: {start_time / 1000} s, End: {end_time / 1000} s")
            
            # Extract and save the segment
            segment = audio[start_time:end_time]
            segment.export(output_file, format="mp3")
            print(f"Saved: {output_file}")

    except Exception as e:
        print(f"Error during splitting audio: {e}")
        sys.exit(1)

# Preprocess timestamps and split audio
def preprocess_and_split_audio(timestamps_with_names, audio_file, output_dir):
    try:
        # Step 5: Split audio based on processed timestamps and names
        split_audio_by_timestamps_and_names(audio_file, timestamps_with_names, output_dir)

    except Exception as e:
        print(f"An error occurred while processing timestamps: {e}")
        sys.exit(1)

# Add error handling and checkpoints
def main():
    try:
        # Step 1: Check for FFmpeg installation
        check_ffmpeg()

        # Step 2: Define URL and file locations
        video_url = input("Enter the YouTube video URL: ")
        output_audio_file = "downloaded_audio.mp3"
        output_directory = "split_audio_parts"
        
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)
        
        # Step 3: Download audio from YouTube
        download_audio_from_youtube(video_url, output_audio_file)

        # Step 4: Read timestamps and names from the provided text file
        timestamps_file = "timestamps.txt"  # Your text file with timestamps and names
        timestamps_with_names = read_timestamps_from_file(timestamps_file)

        # Step 5: Preprocess timestamps and split audio
        preprocess_and_split_audio(timestamps_with_names, output_audio_file, output_directory)

    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
