from video_creator import VideoCreator
import os
from dotenv import load_dotenv

def main():
    # Load environment variables
    load_dotenv()
    
    # Initialize video creator
    creator = VideoCreator()
    
    # Path to the generated audio file
    audio_path = "test_news_audio.mp3"
    
    if not os.path.exists(audio_path):
        print(f"Error: Audio file not found at {audio_path}")
        return
    
    try:
        # Create TikTok video
        output_path = creator.create_tiktok_video(audio_path)
        print(f"✨ Video created successfully at: {output_path}")
    except Exception as e:
        print(f"❌ Error creating video: {str(e)}")

if __name__ == "__main__":
    main() 