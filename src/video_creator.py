import os
import random
from pathlib import Path
from typing import Tuple
from moviepy.editor import VideoFileClip, clips_array, vfx

class VideoCreator:
    def __init__(self):
        self.surfers_dir = "assets/subway_surfers"
        self.output_dir = "output"
        
        # Create output directory if it doesn't exist
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
    
    def create_tiktok_video(self, avatar_video_path: str) -> str:
        """
        Create a TikTok video by combining avatar video with Subway Surfers gameplay.
        
        Args:
            avatar_video_path (str): Path to the avatar video
            
        Returns:
            str: Path to the final video
        """
        try:
            # 1. Load the avatar video
            avatar_clip = VideoFileClip(avatar_video_path)
            
            # 2. Get a random Subway Surfers clip
            surfers_clip = self._get_random_surfers_clip(avatar_clip.duration)
            
            # 3. Resize clips to match TikTok dimensions (1080x1920)
            avatar_resized = self._resize_clip(avatar_clip, (1080, 960))
            surfers_resized = self._resize_clip(surfers_clip, (1080, 960))
            
            # 4. Stack clips vertically
            final_clip = clips_array([[avatar_resized], [surfers_resized]])
            
            # 5. Add some effects
            final_clip = self._add_effects(final_clip)
            
            # 6. Write the final video
            output_path = os.path.join(self.output_dir, f"final_{int(time.time())}.mp4")
            final_clip.write_videofile(output_path, 
                                     codec='libx264', 
                                     audio_codec='aac',
                                     fps=30)
            
            # 7. Clean up
            avatar_clip.close()
            surfers_clip.close()
            
            return output_path
            
        except Exception as e:
            raise Exception(f"Error creating TikTok video: {str(e)}")
    
    def _get_random_surfers_clip(self, duration: float) -> VideoFileClip:
        """
        Get a random Subway Surfers gameplay clip and trim it to match the duration.
        
        Args:
            duration (float): Required duration in seconds
            
        Returns:
            VideoFileClip: The selected and trimmed gameplay clip
        """
        # Get list of available gameplay videos
        gameplay_files = list(Path(self.surfers_dir).glob("*.mp4"))
        if not gameplay_files:
            raise Exception("No Subway Surfers gameplay videos found in assets directory")
        
        # Select a random file
        selected_file = random.choice(gameplay_files)
        
        # Load and trim the clip
        clip = VideoFileClip(str(selected_file))
        
        # If clip is shorter than required duration, loop it
        if clip.duration < duration:
            clip = clip.loop(duration=duration)
        else:
            # Get a random start point that allows for the full duration
            max_start = clip.duration - duration
            start_time = random.uniform(0, max_start)
            clip = clip.subclip(start_time, start_time + duration)
        
        return clip
    
    def _resize_clip(self, clip: VideoFileClip, size: Tuple[int, int]) -> VideoFileClip:
        """
        Resize a video clip while maintaining aspect ratio.
        
        Args:
            clip (VideoFileClip): The clip to resize
            size (Tuple[int, int]): Target size (width, height)
            
        Returns:
            VideoFileClip: Resized clip
        """
        # Resize while maintaining aspect ratio
        return clip.resize(width=size[0])
    
    def _add_effects(self, clip: VideoFileClip) -> VideoFileClip:
        """
        Add visual effects to the video.
        
        Args:
            clip (VideoFileClip): The clip to add effects to
            
        Returns:
            VideoFileClip: Clip with effects
        """
        # Add a slight zoom effect
        clip = clip.fx(vfx.painting, saturation=1.2)
        
        return clip 