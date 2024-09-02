import firebase_admin
from firebase_admin import credentials, db

# Initialize the Firebase Admin SDK
cred = credentials.Certificate('/home/said/Downloads/somo-795b8-firebase-adminsdk-2yniv-ba50e5e974.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://somo-795b8-default-rtdb.firebaseio.com/'  # Replace with your Firebase database URL
})

# Reference to the 'users' node
users_ref = db.reference('users')

# Function to add a user with username and nickname
def add_user(user_id, username, nickname):
    users_ref.child(user_id).set({
        'username': username,
        'nickname': nickname
    })

# Function to get all users
def get_users():
    users = users_ref.get()
    if users:
        for user_id, user_data in users.items():
            print(f"User ID: {user_id}, Username: {user_data['username']}, Nickname: {user_data['nickname']}")
    else:
        print("No users found.")

# Add some users
add_user('user1', 'john_doe', 'Johnny')
add_user('user2', 'jane_smith', 'Janey')

# Retrieve and display users
get_users()
