import os
import argparse
from datetime import datetime
from dotenv import load_dotenv, find_dotenv
from typing import List, Dict

from news_fetcher import NewsFetcher
from story_generator import StoryGenerator
# from avatar_generator import AvatarGenerator
# from video_creator import VideoCreator
# from tiktok_poster import TikTokPoster
from pathlib import Path
from dotenv import load_dotenv
from video_creator import VideoCreator
from test_avatar import test_story  # Import the test story

load_dotenv()

def parse_args():
    parser = argparse.ArgumentParser(description='Generate TikTok news videos with celebrity avatars')
    parser.add_argument('--date', type=str, help='Date to fetch news for (YYYY-MM-DD)',
                       default=datetime.now().strftime('%Y-%m-%d'))
    parser.add_argument('--celebrity', type=str, help='Celebrity avatar to use',
                       choices=['Donald Trump', 'Barack Obama', 'Samuel L Jackson'],
                       default='Barack Obama')
    return parser.parse_args()

def main():
    # Initialize video creator
    video_creator = VideoCreator()
    
    try:
        # Use the Greek audio file
        audio_path = "test_news_audio.mp3"
        
        if not os.path.exists(audio_path):
            print(f"Error: Greek audio file not found at {audio_path}")
            print("Please run test_avatar.py first to generate the Greek audio")
            return
        
        # Create TikTok video with the actual text
        final_video = video_creator.create_tiktok_video(audio_path, test_story)
        print(f"Successfully created video: {final_video}")
        
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        raise

if __name__ == "__main__":
    main() 