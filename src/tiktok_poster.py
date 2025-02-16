import os
from typing import Optional
from TikTokApi import TikTokApi

class TikTokPoster:
    def __init__(self):
        self.api_key = os.getenv('TIKTOK_API_KEY')
        self.api = TikTokApi()
    
    def post_video(self, video_path: str, caption: str) -> str:
        """
        Post a video to TikTok.
        
        Args:
            video_path (str): Path to the video file
            caption (str): Caption for the TikTok post
            
        Returns:
            str: URL of the posted video
        """
        try:
            # Authenticate with TikTok
            self.api.login(api_key=self.api_key)
            
            # Upload the video
            with open(video_path, 'rb') as video_file:
                response = self.api.post_video(
                    video=video_file,
                    description=caption,
                    thumbnail_timestamp=0
                )
            
            # Get the video URL
            video_id = response.json()['video_id']
            video_url = f"https://www.tiktok.com/@{response.json()['author']['unique_id']}/video/{video_id}"
            
            return video_url
            
        except Exception as e:
            raise Exception(f"Error posting to TikTok: {str(e)}")
        
        finally:
            # Always logout
            self.api.logout() 