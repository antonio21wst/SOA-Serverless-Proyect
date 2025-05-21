import json
from config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, REDIRECT_URI, GOOGLE_DISCOVERY_URL, SCOPES


with open('soap_client_test/client_secret_1018285043352-4gs36duirt321bio4nmcssb18ce8d3sd.apps.googleusercontent.com.json') as f:
    google_creds = json.load(f)['web']

GOOGLE_CLIENT_ID = google_creds['client_id']
GOOGLE_CLIENT_SECRET = google_creds['client_secret']
REDIRECT_URI = google_creds['redirect_uris'][0]
GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"
SCOPES = ['openid', 'email', 'profile']
