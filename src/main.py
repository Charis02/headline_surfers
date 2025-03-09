import os
import argparse
from datetime import datetime
from dotenv import load_dotenv, find_dotenv
from typing import List, Dict

from news_fetcher import NewsFetcher
from story_generator import StoryGenerator
from audio_generator import AudioGenerator
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
    args = parse_args()
    
    # Load environment variables
    gemini_api_key = os.getenv('GEMINI_API_KEY')
    elevenlabs_api_key = os.getenv('ELEVENLABS_API_KEY')
    if not gemini_api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set")
    if not elevenlabs_api_key:
        raise ValueError("ELEVENLABS_API_KEY environment variable not set")

    # Initialize components
    news_fetcher = NewsFetcher(api_key=gemini_api_key)
    story_generator = StoryGenerator(api_key=gemini_api_key)
    audio_generator = AudioGenerator(api_key=elevenlabs_api_key)
    video_creator = VideoCreator()
    
    try:
        # 1. Fetch news articles
        print("Fetching news articles...")
        articles = news_fetcher.fetch_articles(args.date)
        if not articles:
            raise Exception(f"No news articles found for date {args.date}")
        print(f"Found {len(articles)} articles")
        
        # 2. Generate story from articles
        print("Generating story...")
        story = story_generator.generate_story(articles, args.date)
        print("Story generated successfully")

        # 3. Create audio from story
        print("Generating audio...")
        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)  # Create output directory if it doesn't exist
        audio_path = os.path.join(output_dir, f"news_audio_{args.date}.mp3")
        audio_generator.create_audio(story, output_file=audio_path)
        if not os.path.exists(audio_path):
            raise Exception(f"Failed to generate audio file at {audio_path}")
        print(f"Audio generated at {audio_path}")
        
        # 4. Create TikTok video
        print("Creating TikTok video...")
        final_video = video_creator.create_tiktok_video(audio_path, story)
        print(f"Successfully created video: {final_video}")
        
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        raise

if __name__ == "__main__":
    main() 