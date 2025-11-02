import requests
import playsound
from mutagen.mp3 import MP3
import time
import os
api_key = os.getenv("TALKBOT_API_KEY")
api_url = "https://api.talkbot.ir/v1/media/text-to-speech/REQ"
file_name = "Say.mp3"
headers = {
    'Authorization': f'Bearer {api_key}'
}
with open("to_say.txt", "r", encoding="utf-8") as f:
    text=f.read()

data = {
    'text': text,
    'server': 'farsi',
    'sound': '3'
}

try:
    response = requests.post(api_url, headers=headers, data=data)

    if response.status_code == 200:
        
        json_data = response.json()
        
        try:
            download_url = json_data['response']['download']
            
            print(f"Download link :{download_url}")

            audio_response = requests.get(download_url)
            
            if audio_response.status_code == 200:
                with open(file_name, 'wb') as f:
                    f.write(audio_response.content)
                try:
                    audio_info = MP3(file_name)
                    duration_seconds = audio_info.info.length
                    playsound.playsound(file_name)
                    time.sleep(duration_seconds + 1)
                    print("Playback finished.")
                except Exception as e:
                    print(f"⚠️ Error playing file: {e}")
                    print("Note: On Linux, you might need to install 'GStreamer' or 'PyGObject'.") 
                print(f"✅ Audio file successfully saved as '{file_name}'.")
            else:
                print(f"Error downloading audio file. Status code: {audio_response.status_code}")

        except KeyError:
            print("Error: Received JSON structure does not match expected format. Download link not found.")
            print(f"Received response: {json_data}") 
            
    else:
        print(f"Error sending initial request. Status code: {response.status_code}") 
        print(f"Error message: {response.text}") 

except requests.exceptions.RequestException as e:
    print(f"Error connecting to API: {e}")
