import os
import time
import requests
from typing import Dict
from elevenlabs import generate, save
from pathlib import Path

class AvatarGenerator:
    def __init__(self):
        self.d_id_api_key = os.getenv('D_ID_API_KEY')
        self.elevenlabs_api_key = os.getenv('ELEVENLABS_API_KEY')
        self.d_id_api_url = "https://api.d-id.com"
        
        # Voice mapping (ElevenLabs voice IDs)
        self.voice_mapping = {
            "Donald Trump": "trump_voice_id",
            "Barack Obama": "obama_voice_id",
            "Samuel L Jackson": "jackson_voice_id",
            "Male Reporter": "male_reporter_voice_id",  # Add appropriate ElevenLabs voice ID
            "Female Reporter": "female_reporter_voice_id"  # Add appropriate ElevenLabs voice ID
        }
        
        # Image mapping (D-ID presenter IDs)
        self.presenter_mapping = {
            "Donald Trump": "trump_presenter_id",
            "Barack Obama": "obama_presenter_id",
            "Samuel L Jackson": "jackson_presenter_id",
            "Male Reporter": "13c0eed0-1b85-4896-9378-5f650e8ee2f1",  # Default D-ID male presenter
            "Female Reporter": "bae3d0dd-6443-4555-9532-6341aa1a9105"  # Default D-ID female presenter
        }
        
    def create_video(self, story: str, celebrity: str) -> str:
        """
        Create a talking head video with the given story and celebrity.
        
        Args:
            story (str): The story to be narrated
            celebrity (str): The celebrity avatar to use
            
        Returns:
            str: Path to the generated video file
        """
        try:
            # 1. Generate audio using ElevenLabs
            audio_path = self._generate_audio(story, celebrity)
            
            # 2. Create talking head video using D-ID
            video_path = self._create_talking_head(audio_path, celebrity)
            
            # 3. Clean up temporary audio file
            Path(audio_path).unlink()
            
            return video_path
            
        except Exception as e:
            raise Exception(f"Error generating avatar video: {str(e)}")
    
    def _generate_audio(self, text: str, celebrity: str) -> str:
        """
        Generate audio using ElevenLabs API.
        
        Args:
            text (str): Text to convert to speech
            celebrity (str): Celebrity voice to use
            
        Returns:
            str: Path to generated audio file
        """
        try:
            voice_id = self.voice_mapping[celebrity]
            
            audio = generate(
                text=text,
                voice=voice_id,
                model="eleven_multilingual_v2",
                language="el"  # Specify Greek language
            )
            
            audio_path = f"temp_{int(time.time())}.mp3"
            save(audio, audio_path)
            
            return audio_path
            
        except Exception as e:
            raise Exception(f"Error generating audio: {str(e)}")
    
    def _create_talking_head(self, audio_path: str, celebrity: str) -> str:
        """
        Create talking head video using D-ID API.
        
        Args:
            audio_path (str): Path to audio file
            celebrity (str): Celebrity avatar to use
            
        Returns:
            str: Path to generated video file
        """
        try:
            # 1. Create talk
            presenter_id = self.presenter_mapping[celebrity]
            
            with open(audio_path, 'rb') as audio_file:
                create_talk_response = requests.post(
                    f"{self.d_id_api_url}/talks",
                    headers={
                        "Authorization": f"Basic {self.d_id_api_key}"
                    },
                    data={
                        "presenter_id": presenter_id,
                        "driver_id": "wav2lip"
                    },
                    files={
                        "audio": audio_file
                    }
                ).json()
            
            talk_id = create_talk_response['id']
            
            # 2. Wait for video generation to complete
            while True:
                status_response = requests.get(
                    f"{self.d_id_api_url}/talks/{talk_id}",
                    headers={"Authorization": f"Basic {self.d_id_api_key}"}
                ).json()
                
                if status_response['status'] == 'done':
                    # 3. Download the video
                    video_url = status_response['result_url']
                    video_path = f"avatar_{int(time.time())}.mp4"
                    
                    with requests.get(video_url, stream=True) as r:
                        r.raise_for_status()
                        with open(video_path, 'wb') as f:
                            for chunk in r.iter_content(chunk_size=8192):
                                f.write(chunk)
                    
                    return video_path
                
                elif status_response['status'] == 'error':
                    raise Exception(f"D-ID API error: {status_response.get('error', 'Unknown error')}")
                
                time.sleep(5)  # Wait before checking again
                
        except Exception as e:
            raise Exception(f"Error creating talking head video: {str(e)}") 