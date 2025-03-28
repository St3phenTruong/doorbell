import RPi.GPIO as GPIO
import subprocess
import os
import signal
import time
import uuid
import firebase
import cloudinary
import cloudinary.uploader
import names
import datetime

chat_id = str(uuid.uuid4()) #tao. ID room ngau nhien
link = "http://meet.jit.si/"+str(chat_id)
thoigian = datetime.datetime.now() #ghi lai. thoi` diem? hien. tai.
call_face = False

# Configure Cloudinary 
cloudinary.config(
    cloud_name="dyrabqcno",
    secure=True,
    api_key="885437657119333",
    api_secret="JrlYz1bz-cKtqwtLJ7RYxetVLmU"
)

# Upload the image
response = cloudinary.uploader.upload(
    "buglarly.jpg",  # Path to your image
    public_id=names.get_full_name(),        # Optional: specify a unique ID for the file
    overwrite=True            # Optional: overwrite if the same public ID exists
)

# Print the response
print("Uploaded Successfully!")
print(f"URL: {response['secure_url']}")

# Firebase configuration
config = {
  "apiKey": "AIzaSyAamS-omT7i-1fFFuwHr5k8_ILt0ptNl3E",
  "authDomain": "pidrowsiness-277a4.firebaseapp.com",
  "databaseURL": "https://pidrowsiness-277a4-default-rtdb.firebaseio.com",
  "projectId": "pidrowsiness-277a4",
  "storageBucket": "pidrowsiness-277a4.appspot.com",
  "messagingSenderId": "443787716450",
  "appId": "1:443787716450:web:c7033070895e50b0e56e3b",
  "measurementId": "G-KBBZSE34Y3"
}

# Instantiates a Firebase app
app = firebase.initialize_app(config)
db = app.database()

# Gui? Link Jitsi room, link hinh` anh?, thoi` gian len Firebase
data = {"Link_Jitsi_Meet": link,
"Link_image": response['secure_url'],
"Time": thoigian.strftime("%c")}
db.child("Status").set(data)
# Add a 0.1-second delay between pushes
time.sleep(0.1)
print(data)

#set up button
BUTTON = 17
DEBOUNCE_TIME = 0.2  # Debounce time in seconds
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Pull-up to handle button state reliably

# Set up lop' cuoc. goi.
class VideoChat:
    def __init__(self, chat_id):
        self.chat_id = chat_id
        self._process = None

    def get_chat_url(self):
        return f"http://meet.jit.si/{self.chat_id}"

    def start(self):
        if not self._process:
            print(f"Accessing Jitsi room: {self.get_chat_url()}")
            set_default_audio_input("Built-in audio stereo")  # Set default audio input
            self._process = subprocess.Popen(["firefox", "--kiosk", self.get_chat_url()])
        else:
            print("Video chat already started.")

    def end(self):
        if self._process:
            os.kill(self._process.pid, signal.SIGTERM)
            self._process = None
            print("Video chat ended.")

# Function to set the default audio input device
def set_default_audio_input(device_name):
    # List all sources
    sources = subprocess.check_output(["pactl", "list", "short", "sources"]).decode()
    # Find the line with the device name
    for line in sources.splitlines():
        if device_name in line:
            # Extract the source index (first column)
            source_index = line.split()[0]
            # Set the default source
            subprocess.call(["pactl", "set-default-source", source_index])
            print(f"Default audio input set to {device_name}")
            break
    else:
        print(f"Audio input device {device_name} not found")

# Set up ham` chinh' cua? chuong trinh`
def jitsi():
    video_chat = VideoChat(chat_id)
    print("Ready for button press.")
    video_chat.start() #mo? cuoc. goi.
    
    #Nhan' nut' se~ out room Jitsi
    try:
        while True:
            state = GPIO.input(BUTTON)
            if not state:  # Button pressed
                print("Button pressed.")
                time.sleep(DEBOUNCE_TIME)  # Debounce delay

                print("Ending video chat...")
                call_face = True
                video_chat.end()
                break  # Exit the loop after ending the chat

            time.sleep(0.1)  # Polling delay
    except KeyboardInterrupt:
        print("Exiting program.")
    finally:
        GPIO.cleanup()
        if video_chat._process:
            video_chat.end()
        print("Program exited.")

if __name__ == "__main__":
    jitsi()
    
    #quay lai. chay. file pi_face_official.py
    subprocess.Popen(["python", "pi_face_official.py"])
    pid = os.getpid()
    call_jitsi = False
    os.kill(pid, signal.SIGTERM)