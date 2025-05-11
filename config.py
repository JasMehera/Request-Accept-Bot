import os
from typing import List

API_ID = os.environ.get("API_ID", "28713982")
API_HASH = os.environ.get("API_HASH", "237e15f7c006b10b4fa7c46fee7a5377")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "7742892578:AAEgE8pnKOvcBs00SfCePmRka7MbU0xuBBM")
ADMIN = int(os.environ.get("ADMIN", "7518139247"))

LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL", "-1002100963256"))
NEW_REQ_MODE = os.environ.get("NEW_REQ_MODE", "True").lower() == "true"  # Set "True" For accept new requests

DB_URI = os.environ.get("DB_URI", "mongodb+srv://f00il:animeotaku109@cluster0.qhc7amc.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
DB_NAME = os.environ.get("DB_NAME", "RequestAcceptBot")

IS_FSUB = os.environ.get("IS_FSUB", "False").lower() == "true"  # Set "True" For Enable Force Subscribe
AUTH_CHANNELS = list(map(int, os.environ.get("AUTH_CHANNEL", "").split())) # Add Multiple channel ids

APPROVED_BUTTON_URL = "https://t.me/Union_Botss"
APPROVED_IMAGE_URL = "https://envs.sh/4f4.jpg"

START_IMAGE = "https://envs.sh/4fO.jpg"  # replace with your image URL
