#!/usr/bin/env python3

import time
import requests
import json

UID = "u-s4t2ud-72edb592cf85d446ddd65b0417a066be9259714a3aab7eef4fba5dbc04c788b6"
SECRET = "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"

def post42(url, payload):
    url = "https://api.intra.42.fr" + url
    payload = payload
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    return response.json()

def get42(url, payload):
    url = "https://api.intra.42.fr" + url
    payload = payload
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    return response.json()

wtoken = post42("/oauth/token", {"grant_type": "client_credentials", \
                                "client_id": UID, "client_secret": SECRET})
campus_users = []
temp = []

campus_users_general = '/v2/campus/51'
campus_users_total = get42(campus_users_general, {"access_token": wtoken["access_token"]})
total_users = campus_users_total["users_count"]

total_pages = ( total_users // 100 + 1 ) + 1

print(f"Total users: {total_users} Total pages: {total_pages}")
print("Please wait while data from API is retrieved...")

for i in range(1, total_pages):  
    campus_users += get42("/v2/campus/51/users?page[number]=" + str(i) + "&page[size]=100", \
                                                   {"access_token": wtoken["access_token"]})

for user in campus_users:
    temp.append({
        "login": user.get("login"),  
        "correction_point":  user.get("correction_point"),
        "pool_year": user.get("pool_year"),
        "location": user.get("location"),  
        "updated_at": user.get("updated_at").split("T")[1].split(".")[0],
        "wallet": user.get("wallet")
    })
for user in temp:
    print(user.get("login"))