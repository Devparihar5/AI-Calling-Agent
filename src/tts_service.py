import os
import asyncio
import edge_tts
import tempfile
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class TextToSpeech:
    def __init__(self):
        """Initialize TTS service"""
        self.voice = os.environ.get('TTS_VOICE')
        if not self.voice:
            print("TTS_VOICE not found in environment variables, using default")
            self.voice = 'en-US-JennyNeural'
            
        self.output_dir = os.environ.get('TTS_OUTPUT_DIR')
        if not self.output_dir:
            self.output_dir = '/tmp'
            
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
    
    def text_to_speech(self, text, output_file=None):
        """Convert text to speech and save to file"""
        if not output_file:
            # Create a temporary file if no output file is specified
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3', dir=self.output_dir)
            output_file = temp_file.name
            temp_file.close()
        
        # Run the async TTS function
        asyncio.run(self._async_tts(text, output_file))
        
        return output_file
    
    async def _async_tts(self, text, output_file):
        """Async function to generate speech"""
        communicate = edge_tts.Communicate(text, self.voice)
        await communicate.save(output_file)
    
    def text_to_speech_stream(self, text):
        """Convert text to speech and return as stream"""
        # For streaming, we'll first save to a file and then read it
        output_file = self.text_to_speech(text)
        
        # Read the file and return its contents
        with open(output_file, 'rb') as f:
            audio_data = f.read()
        
        # Clean up the temporary file
        os.unlink(output_file)
        
        return audio_data
