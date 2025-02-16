import os
import argparse
from datetime import datetime
from dotenv import load_dotenv
from typing import List, Dict

from news_fetcher import NewsFetcher
from story_generator import StoryGenerator
from avatar_generator import AvatarGenerator
from video_creator import VideoCreator
from tiktok_poster import TikTokPoster

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
    
    # Initialize components
    news_fetcher = NewsFetcher()
    story_generator = StoryGenerator()
    avatar_generator = AvatarGenerator()
    video_creator = VideoCreator()
    tiktok_poster = TikTokPoster()
    
    try:
        # 1. Fetch top Greek news articles
        articles = news_fetcher.fetch_articles(args.date)
        
        # 2. Generate Gen Z story from articles
        story = story_generator.generate_story(articles)
        
        # 3. Create avatar video
        avatar_video = avatar_generator.create_video(story, args.celebrity)
        
        # 4. Combine with Subway Surfers footage
        final_video = video_creator.create_tiktok_video(avatar_video)
        
        # 5. Post to TikTok
        video_url = tiktok_poster.post_video(final_video, story[:100])  # Use first 100 chars as caption
        
        print(f"Successfully created and posted video: {video_url}")
        
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        raise

if __name__ == "__main__":
    main() 