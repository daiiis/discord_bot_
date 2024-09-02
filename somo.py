

import firebase_admin
from firebase_admin import credentials, db
import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime, timedelta
import requests
from requests.auth import HTTPBasicAuth


TOKEN = 'MTI3ODY1NzgzNTM0MDc5MTg1OQ.G6TUTl.B29Q7wV_-yB75iRvefd_m09oL2Q5E04rq-t6bk'
CLIENT_ID = 'u-s4t2ud-72edb592cf85d446ddd65b0417a066be9259714a3aab7eef4fba5dbc04c788b6'
REDIRECT_URI = 'http://localhost:8000/callback'

cred = credentials.Certificate('/home/said/Downloads/somo-795b8-firebase-adminsdk-2yniv-ba50e5e974.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://somo-795b8-default-rtdb.firebaseio.com/'
})


users_ref = db.reference('users')

def add_user(user_id, username, nickname):
    users_ref.child(user_id).set({
        'username': username,
        'nickname': nickname
    })

def get_user(user_id):
    user = users_ref.child(user_id).get()
    if user:
        return user
    else:
        return None

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='/', intents=intents)


available_times = ['17:00', '18:00', '19:00']
available_sports = ['football', 'volleyball', 'handball', 'basketball']
reservations = {}


def is_valid_time(time):
    return time in available_times

def is_valid_sport(sport):
    return sport in available_sports

def parse_date(date_str):
    try:
        date_str = date_str.strip('/')
        return datetime.strptime(date_str, '%Y/%m/%d')
    except ValueError:
        return None

def is_date_within_range(date_obj):
    today = datetime.now().date()
    end_date = today + timedelta(days=7)
    return today <= date_obj.date() <= end_date

def get_reservation_key(date, time, sport):
    return f"{date}_{time}_{sport}"

async def send_error(interaction, message):
    await interaction.response.send_message(message, ephemeral=True)

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands")
    except Exception as e:
        print(f"Error syncing commands: {e}")

@bot.tree.command(name="reserve", description="Reserve a spot")
@app_commands.describe(date="The date of reservation (YYYY/MM/DD)", time="The time of reservation", sport="The sport to reserve")
async def reserve_command(interaction: discord.Interaction, date: str, time: str, sport: str):
    if not is_valid_time(time):
        await send_error(interaction, "Invalid time. Please choose a time from 17:00, 18:00, or 19:00.")
        return

    if not is_valid_sport(sport):
        await send_error(interaction, "Invalid sport. Please choose from football, volleyball, handball, and basketball.")
        return

    date_obj = parse_date(date)
    if not date_obj:
        await send_error(interaction, "Invalid date format. Please use YYYY/MM/DD.")
        return

    if not is_date_within_range(date_obj):
        await send_error(interaction, "Invalid date. Please choose a date between today and a week from now.")
        return

    reservation_key = get_reservation_key(date_obj.date(), time, sport)
    if reservation_key in reservations:
        await send_error(interaction, f"Time slot {date} {time} for {sport} is already reserved.")
        return

    reservations[reservation_key] = interaction.user.mention
    await interaction.response.send_message(f"Reserved {date} {time} for {sport} for {interaction.user.mention}!")

@bot.tree.command(name="cancel", description="Cancel a reservation")
@app_commands.describe(date="The date of reservation (YYYY/MM/DD)", time="The time of reservation", sport="The sport to cancel")
async def cancel_command(interaction: discord.Interaction, date: str, time: str, sport: str):
    if not (date and time and sport):
        await send_error(interaction, "Please provide date, time, and sport.")
        return

    if not is_valid_time(time):
        await send_error(interaction, "Invalid time. Please choose a time from 17:00, 18:00, or 19:00.")
        return

    if not is_valid_sport(sport):
        await send_error(interaction, "Invalid sport. Please choose from football, volleyball, handball, and basketball.")
        return

    date_obj = parse_date(date)
    if not date_obj:
        await send_error(interaction, "Invalid date format. Please use YYYY/MM/DD.")
        return

    reservation_key = get_reservation_key(date_obj.date(), time, sport)

    if reservation_key not in reservations or interaction.user.mention != reservations[reservation_key]:
        await send_error(interaction, f"You don't have a reservation for {date} {time} for {sport}.")
        return

    del reservations[reservation_key]
    await interaction.response.send_message(f"Canceled reservation for {date} {time} for {sport}.")

@bot.tree.command(name="list", description="List reservation status")
@app_commands.describe(date="The date of reservation (YYYY/MM/DD)", sport="The sport to check")
async def list_command(interaction: discord.Interaction, date: str, sport: str):
    if not (date and sport):
        await send_error(interaction, "Please provide date and sport.")
        return

    if not is_valid_sport(sport):
        await send_error(interaction, "Invalid sport. Please choose from football, volleyball, handball, and basketball.")
        return

    date_obj = parse_date(date)
    if not date_obj:
        await send_error(interaction, "Invalid date format. Please use YYYY/MM/DD.")
        return

    messages = []
    for time in available_times:
        reservation_key = get_reservation_key(date_obj.date(), time, sport)
        status = "Reserved" if reservation_key in reservations else "Not Reserved"
        messages.append(f"Time: **{time}** - Status: **{status}**")

    embed = discord.Embed(
        title="Reservation Status",
        description=f"Date: **{date}**\nSport: **{sport}**\n\n" + "\n".join(messages),
        color=discord.Color.blue()
    )
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="sing_in", description="Sign in to out Lak server")
async def sing_in_command(interaction: discord.Interaction):
    embed = discord.Embed(
        title="Sign in to 42",
        description="Please click the link below to sign in to 42. This will redirect you to your 42 account.",
        color=discord.Color.blue()
    )
    user_info = str(interaction.user.id) +"$"+  interaction.user.name
    print(user_info)
    oauth_url = (
        f"https://api.intra.42.fr/oauth/authorize?"
        f"client_id={CLIENT_ID}&"
        f"redirect_uri={REDIRECT_URI}&"
        f"response_type=code&"
        f"state={user_info}&"
    )
    await interaction.response.send_message(f"Sign in to 42 using this link: {oauth_url}")
    print(get_user("576891892294352896"))

bot.run(TOKEN)






