import requests
import sys
from config import TALKBOT_API_URL , TALKBOT_API_KEY

def speak_text_from_file(input_file = "to_say.txt"):

    api_key = TALKBOT_API_KEY
    api_url = TALKBOT_API_URL
    file_name = "Say.mp3"
    
    headers = {
        'Authorization': f'Bearer {api_key}'
    }

    try:
        with open(input_file, "r", encoding="utf-8") as f:
            text = f.read()
            if not text.strip():
                print(f"Warning: The file '{input_file}' is empty. Nothing to say.")
                sys.exit(0)
    except FileNotFoundError:
        print(f"Error: The input file '{input_file}' was not found.")
        sys.exit(1)
    
    data = {
        'text': text,
        'server': 'farsi',
        'sound': '3'
    }

    print("Sending request to generate audio...")
    
    try:
        response = requests.post(api_url, headers=headers, data=data)

        if response.status_code == 200:
            json_data = response.json()
            
            try:
                download_url = json_data['response']['download']
                print(f"Download link: {download_url}")

                audio_response = requests.get(download_url)
                
                if audio_response.status_code == 200:
                    with open(file_name, 'wb') as f:
                        f.write(audio_response.content)
                    
                    print(f"✅ Audio file successfully saved as '{file_name}'.")    
                    return True        
                else:
                    print(f"Error downloading audio file. Status code: {audio_response.status_code}")
                    return False

            except KeyError:
                print("Error: Received JSON structure does not match expected format.")
                print(f"Received response: {json_data}") 
                return False

                
        else:
            print(f"Error sending initial request. Status code: {response.status_code}") 
            print(f"Error message: {response.text}") 
            return False


    except requests.exceptions.RequestException as e:
        print(f"Error connecting to API: {e}")
        return False

if __name__ == "__main__":
    speak_text_from_file()
