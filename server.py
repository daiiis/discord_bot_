from flask import Flask, request, redirect
import requests
import firebase_admin
from firebase_admin import credentials, db


cred = credentials.Certificate('/home/said/Downloads/somo-795b8-firebase-adminsdk-2yniv-ba50e5e974.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://somo-795b8-default-rtdb.firebaseio.com/'
})

app = Flask(__name__)

CLIENT_ID = 'u-s4t2ud-72edb592cf85d446ddd65b0417a066be9259714a3aab7eef4fba5dbc04c788b6'
CLIENT_SECRET = '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'
REDIRECT_URI = 'http://localhost:8000/callback'

users_ref = db.reference('users')

def add_user(user_id, username, nickname):
    users_ref.child(user_id).set({
        'username': username,
        'nickname': nickname
    })
@app.route('/callback')
def callback():
    code = request.args.get('code')
    user_details = request.args.get('state')

    token_url = "https://api.intra.42.fr/oauth/token"
    data = {
        'grant_type': 'authorization_code',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'code': code,
        'redirect_uri': REDIRECT_URI
    }

    response = requests.post(token_url, data=data)
    token_data = response.json()
    access_token = token_data.get('access_token')

    user_info_url = "https://api.intra.42.fr/v2/me"
    headers = {'Authorization': f'Bearer {access_token}'}
    user_response = requests.get(user_info_url, headers=headers)

    if user_response.status_code == 200:
        user_data = user_response.json()
        username = user_data.get('login')
        print(username)
        user_info = {
            "userId": user_details[0:user_details.find("$")],
            "nickname": user_details[user_details.find("$")+1:],
            "username": username
        }
        add_user(user_info["userId"], user_info["username"], user_info["nickname"])
        
        
        # user_details['username'] = username
        # print(user_details.nickname)
        
        return f"Successfully signed in! Username: {username}"
    else:
        return "Failed to fetch user data."

if __name__ == '__main__':
    app.run(port=8000)
