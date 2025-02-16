import os
import random
import time
from pathlib import Path
from typing import Tuple
import requests
import ffmpeg
import whisper
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import tempfile
import re

class VideoCreator:
    def __init__(self):
        self.surfers_dir = "assets/subway_surfers"
        self.output_dir = "output"
        self.temp_dir = "temp"
        
        # Create necessary directories
        for dir_path in [self.surfers_dir, self.output_dir, self.temp_dir]:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
        
        # Initialize whisper model for transcription
        self.model = whisper.load_model("base")
    
    def get_video_duration(self, video_path: str) -> float:
        """Get the duration of a video file."""
        probe = ffmpeg.probe(video_path)
        video_info = next(s for s in probe['streams'] if s['codec_type'] == 'video')
        return float(video_info['duration'])
    
    def get_random_start_time(self, video_path: str, required_duration: float) -> float:
        """Get a random start time that allows for the required duration."""
        total_duration = self.get_video_duration(video_path)
        if total_duration < required_duration:
            return 0.0  # If video is shorter, start from beginning and it will loop
        return random.uniform(0, total_duration - required_duration)
    
    def check_video_exists(self) -> str:
        """Check if the Subway Surfers video exists."""
        video_path = os.path.join(self.surfers_dir, "gameplay.mp4")
        if not os.path.exists(video_path):
            raise Exception(
                "Subway Surfers video not found. Please add the video file to "
                "assets/subway_surfers/gameplay.mp4"
            )
        return video_path
    
    def generate_captions(self, audio_path: str) -> list:
        """Generate captions from audio file using Whisper."""
        print("Generating captions...")
        result = self.model.transcribe(audio_path, language="el")  # Specify Greek language
        return result["segments"]
    
    def create_caption_image(self, text: str, width: int, height: int) -> str:
        """Create a caption image with the given text."""
        # Create a transparent image
        image = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        
        # Split long text into multiple lines (max 30 chars per line)
        words = text.split()
        lines = []
        current_line = []
        current_length = 0
        
        for word in words:
            if current_length + len(word) + 1 <= 30:  # +1 for space
                current_line.append(word)
                current_length += len(word) + 1
            else:
                if current_line:  # Add the current line if it exists
                    lines.append(' '.join(current_line))
                current_line = [word]
                current_length = len(word)
        
        if current_line:  # Add the last line
            lines.append(' '.join(current_line))
        
        # Join lines with newlines
        text = '\n'.join(lines)
        
        # Start with a large font size but not too large
        font_size = 120  # Slightly smaller initial size
        min_font_size = 60  # Don't go smaller than this
        
        try:
            font = ImageFont.truetype("Arial", font_size)
        except:
            print("Warning: Arial font not found, using default font")
            font = ImageFont.load_default()
        
        # Calculate text size and position (use getbbox for multiline text)
        bbox = draw.multiline_textbbox((0, 0), text, font=font, align='center')
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # Scale down if text is too wide, but not below minimum
        if text_width > width - 100:  # Leave more padding
            scale_factor = (width - 100) / text_width
            new_size = int(font_size * scale_factor)
            font_size = max(new_size, min_font_size)
            try:
                font = ImageFont.truetype("Arial", font_size)
            except:
                font = ImageFont.load_default()
            bbox = draw.multiline_textbbox((0, 0), text, font=font, align='center')
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
        
        # Center text horizontally and position near bottom
        x = (width - text_width) / 2
        y = height * 0.75  # Position a bit higher for multiline
        
        print(f"\nCreating caption image:")
        print(f"Text: {text}")
        print(f"Font size: {font_size}")
        print(f"Position: x={x}, y={y}")
        print(f"Dimensions: width={text_width}, height={text_height}")
        
        # Create a solid black background box
        padding = 40
        bg_left = 0  # Full width background
        bg_right = width
        bg_top = y - padding
        bg_bottom = y + text_height + padding
        draw.rectangle([bg_left, bg_top, bg_right, bg_bottom], fill=(0, 0, 0, 255))  # Solid black
        
        # Draw text with thick outline
        outline_color = "black"
        text_color = "white"  # Pure white for maximum contrast
        outline_width = 12  # Very thick outline
        
        # Draw outline in all directions
        for dx in range(-outline_width, outline_width + 1, 4):
            for dy in range(-outline_width, outline_width + 1, 4):
                draw.multiline_text((x + dx, y + dy), text, font=font, fill=outline_color, align='center')
        
        # Draw main text
        draw.multiline_text((x, y), text, font=font, fill=text_color, align='center')
        
        # Save with unique timestamp
        temp_path = os.path.join(self.temp_dir, f"caption_{int(time.time()*1000)}.png")
        image.save(temp_path, "PNG")
        print(f"Saved caption image to: {temp_path}")
        
        # Verify the image was created and has content
        if os.path.exists(temp_path):
            size = os.path.getsize(temp_path)
            print(f"Caption file size: {size} bytes")
            
            # Load and verify the image
            test_img = Image.open(temp_path)
            print(f"Image size: {test_img.size}")
            print(f"Image mode: {test_img.mode}")
        else:
            print("Warning: Caption file was not created!")
        
        return temp_path
    
    def create_tiktok_video(self, audio_path: str, text: str) -> str:
        """Create a TikTok video by combining audio with Subway Surfers gameplay."""
        try:
            # 1. Check if video exists
            video_path = self.check_video_exists()
            
            # 2. Get timing from audio transcription
            segments = self.generate_captions(audio_path)
            
            # 3. Split text into sentences
            text = ' '.join(text.split())  # Normalize spacing
            sentences = []
            for part in re.split('[.!?]', text):
                part = part.strip()
                if part:
                    sentences.append(part)
            
            # 4. Match sentences with audio segments
            captions = []
            for i, sentence in enumerate(sentences):
                if i < len(segments):
                    # Use timing from audio segments
                    captions.append({
                        'text': sentence,
                        'start': segments[i]['start'],
                        'end': segments[i]['end']
                    })
                else:
                    # If we have more sentences than segments, estimate timing
                    last_end = captions[-1]['end'] if captions else 0
                    captions.append({
                        'text': sentence,
                        'start': last_end,
                        'end': last_end + 3.0  # Default 3 seconds
                    })
            
            # 5. Get video duration from audio
            probe = ffmpeg.probe(audio_path)
            audio_duration = float(probe['streams'][0]['duration'])
            
            # 6. Get random start time in the video
            start_time = self.get_random_start_time(video_path, audio_duration)
            print(f"Starting video at {start_time:.2f} seconds")
            
            # 7. Prepare video input with start time
            video = ffmpeg.input(video_path, ss=start_time)
            
            # 8. Scale and pad video to TikTok dimensions (1080x1920)
            video = (
                ffmpeg
                .filter(video, 'scale', 1080, -1)  # Scale width to 1080, maintain aspect ratio
                .filter('pad', 1080, 1920, '(ow-iw)/2', '(oh-ih)/2', color='black')  # Add black padding
            )
            
            # 9. Trim or loop video to match audio duration
            video = ffmpeg.filter(video, 'loop', loop=0, size=str(int(audio_duration)))
            video = ffmpeg.filter(video, 'trim', duration=audio_duration)
            
            # 10. Add captions with fade effects
            caption_files = []
            print("\nProcessing captions:")
            for i, segment in enumerate(captions):
                print(f"\nCaption {i+1}:")
                print(f"Text: {segment['text']}")
                print(f"Time: {segment['start']:.2f}s to {segment['end']:.2f}s")
                
                caption_path = self.create_caption_image(segment['text'], 1080, 1920)
                caption_files.append(caption_path)
                
                # Add fade in/out effects
                overlay = ffmpeg.input(caption_path)
                overlay = ffmpeg.filter(overlay, 'fade', type='in', duration=0.2, start_time=segment['start'])
                overlay = ffmpeg.filter(overlay, 'fade', type='out', duration=0.2, start_time=segment['end']-0.2)
                
                video = ffmpeg.overlay(video, overlay,
                                     enable=f'between(t,{segment["start"]},{segment["end"]})')
            
            # 11. Add audio
            audio = ffmpeg.input(audio_path)
            
            # 12. Combine everything with higher bitrate
            output_path = os.path.join(self.output_dir, f"final_{int(time.time())}.mp4")
            stream = ffmpeg.output(video, audio, output_path,
                                 vcodec='libx264',
                                 acodec='aac',
                                 video_bitrate='6M',  # Higher bitrate
                                 audio_bitrate='192k',
                                 r=30)
            
            # 13. Run the FFmpeg command
            print("\nExecuting FFmpeg command...")
            ffmpeg.run(stream, overwrite_output=True)
            
            # 14. Keep temporary files for debugging
            print("\nTemporary caption files (not deleted for debugging):")
            for file in caption_files:
                if os.path.exists(file):
                    print(f"- {file} ({os.path.getsize(file)} bytes)")
            
            return output_path
            
        except Exception as e:
            print(f"\nError creating TikTok video: {str(e)}")
            raise 