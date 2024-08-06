import openai
from django.conf import settings
from deepgram import DeepgramClient, DeepgramClientOptions
from twilio.rest import Client as TwilioClient
from pymongo.mongo_client import MongoClient

def openai_client():
    openai.api_key = settings.OPEN_AI_KEY
    return openai

def twilio_client():
    client = TwilioClient(settings.TWILIO_SID, settings.TWILIO_KEY)
    return client

def deepgram_client():
    options = DeepgramClientOptions(options={"keepalive": "true"})
    client = DeepgramClient(settings.DEEPGRAM_KEY, config=options)
    return client

def get_db():
    client = MongoClient(settings.DB_URL)
    db = client.get_database()
    return db