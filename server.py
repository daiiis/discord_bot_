from flask import Flask, request
import requests
import firebase_admin
from firebase_admin import credentials, db
from dotenv import load_dotenv
import os

load_dotenv()

cred = credentials.Certificate(os.getenv('FIREBASE_CREDENTIALS_PATH'))
firebase_admin.initialize_app(cred, {
    'databaseURL': os.getenv('FIREBASE_DATABASE_URL')
})

app = Flask(__name__)

CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
REDIRECT_URI = os.getenv('DISCORD_LINK')

users_ref = db.reference('users')

def add_user(user_id, username, nickname):
    """Add a user to Firebase Realtime Database."""
    users_ref.child(user_id).set({
        'username': username,
        'nickname': nickname
    })

@app.route('/callback')
def callback():
    """Handle OAuth callback and store user info."""
    code = request.args.get('code')
    user_details = request.args.get('state')

    if not code or not user_details:
        return "Missing code or user details.", 400

    token_url = "https://api.intra.42.fr/oauth/token"
    data = {
        'grant_type': 'authorization_code',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'code': code,
        'redirect_uri': REDIRECT_URI
    }

    try:
        response = requests.post(token_url, data=data)
        response.raise_for_status()
        token_data = response.json()
        access_token = token_data.get('access_token')
    except requests.RequestException as e:
        return f"Error fetching access token: {e}", 500

    user_info_url = "https://api.intra.42.fr/v2/me"
    headers = {'Authorization': f'Bearer {access_token}'}
    try:
        user_response = requests.get(user_info_url, headers=headers)
        user_response.raise_for_status()
        user_data = user_response.json()
        username = user_data.get('login')
    except requests.RequestException as e:
        return f"Error fetching user info: {e}", 500

    user_id, nickname = user_details.split("$", 1)
    add_user(user_id, username, nickname)

    return f"Successfully signed in! Username: {username}"

if __name__ == '__main__':
    app.run(port=8000)
