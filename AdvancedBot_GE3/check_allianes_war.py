import os, json, time, threading
import discord
from discord import channel
from discord import app_commands
from discord.ui import Button
from discord.ext import commands
from datetime import datetime, timedelta, timezone
from itertools import islice
import typing
from discord.ext import tasks
import asyncio
import aiohttp
from dotenv import load_dotenv

load_dotenv()

# class files imports
from database import database
from utility import utility_commands
from dropdown import dropdown
from button import button
# from database_Alex import database_Alex

# define class variables
db_operations = database.DatabaseConnection()
utility_operations = utility_commands.utilityOperations()
# db_Alex = database_Alex.DatabaseConnection()

# #########################
# ####### VARIABLES #######
# #########################

# global variables
# ALLIANCE_NAME = "Galactic Empire II"
ALLIANCE_NAME = "Galactic EmpireIII" 
# GUILD_ID = 1072190344835387392 # GE2
GUILD_ID = 1192245809966751794 # GE3
# CHANNEL_ID = 1252919160850092042  # GE2
CHANNEL_ID = 1262692387470315560 # GE3
CHANNEL_ID_COORDS = 1261682800885764146
# CHANNEL_ID_WAR_CHAT = 1078303407170916362 # GE2
CHANNEL_ID_WAR_CHAT = 1192247627077656576 # GE3
CHANNEL_ID_ATTACKLOG = 1254420671417679952
global regentime
regentime = 3
global points
points = 0
global sum_for_war
sum_for_war = 0
global sum_against_war
sum_against_war = 0
global top_5_least_downtime
top_5_least_downtime = {}
global info_data
info_data = 0
global warpoints
warpoints = {
      1: 100,
      2: 200,
      3: 300,
      4: 400,
      5: 600,
      6: 1000,
      7: 1500,
      8: 2000,
      9: 2500
  }
API_URL = "https://api.galaxylifegame.net/Alliances/get?name="
PATH = "/root/GalaxyLifeBot/AdvancedBot_GE3/JSONS/"
WAR_INFO = "war_info.json"
API_ID = "https://api.galaxylifegame.net/Users/get?id="
API_NAME = "https://api.galaxylifegame.net/Users/name?name="
API_ATTACKLOG = "https://lb.galaxylifeserver.net/api/async/attackLog?signed_request="
API_STATS = "https://api.galaxylifegame.net/Users/stats?id="
API_LB = "https://api.galaxylifegame.net/Alliances/warpointLb"
# General_role_id = 1072196892559147018 #GE2
General_role_id = 1192250005654880316 #GE3
# Captain_role_id = 1072196473334280283 #GE2
Captain_role_id = 1192246304349368340 #GE3
online_players = {}
global war_ready
war_ready = False





async def main():
    check_alliances.start()  # Start the periodic task
    while True:
        await asyncio.sleep(3600)  # Keep the script running

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())













def process_alliance_data(alliance, alliance_data):
    # alliance = collection.find()
    # alliance_data = API response
    alliance_name = alliance["Name"]
    in_war = alliance_data.get("InWar", False)
    opponent = alliance_data.get("OpponentAllianceId", "")
    current_war_points = alliance_data.get("WarPoints", 0)
    now = datetime.now()

    alliances_collection = db_operations.return_collection("alliances")

    war_duration = timedelta(days=3)

    # Check if a new war has started
    if in_war and not alliance["InWar"]:
        # War started, store initial war points and timestamp
        alliances_collection.update_one(
            {"Name": alliance_name},
            {"$set": {"OpponentAllianceId":opponent,"InWar": True, "initialWarPoints": current_war_points, "warStartTime": now}}
        )
    elif in_war:
        # Calculate war points gained since the war started
        initial_war_points = alliance.get("initialWarPoints", 0)
        points_gained = current_war_points - initial_war_points

        # Check if the war has ended
        war_start_time = alliance.get("warStartTime")
        if war_start_time:
            if isinstance(war_start_time, str):
                war_start_time = datetime.strptime(war_start_time, "%Y-%m-%dT%H:%M:%S.%fZ")

            time_elapsed = now - war_start_time
            remaining_time = war_duration - time_elapsed

            if remaining_time <= timedelta(0):
                # War ended, reset InWar status, points gained, and remaining time
                alliances_collection.update_one(
                    {"Name": alliance_name},
                    {"$set": {"InWar": False, "warStartTime": None, "initialWarPoints": None, "pointsGained": 0, "remainingTime": None}}
                )
            else:
                # Update war points gained and remaining time (in seconds)
                alliances_collection.update_one(
                    {"Name": alliance_name},
                    {"$set": {"OpponentAllianceId":opponent,"pointsGained": points_gained, "remainingTime": int(remaining_time.total_seconds())}}
                )
    else:
        # War has ended, reset pointsGained to 0 and remainingTime to None
        # Update LastUpdate time and current war points if not in war
        alliances_collection.update_one(
            {"Name": alliance_name},
            {"$set": {"OpponentAllianceId":"","pointsGained": 0, "remainingTime": None, "LastUpdate": now, "warpoints": current_war_points, "InWar": False}}
        )

@tasks.loop(minutes=1)
async def check_alliances():
    try:
        alliances = db_operations.get_all_alliances()

        async with aiohttp.ClientSession() as session:
            for alliance in alliances:
                alliance_name = alliance["Name"]
                async with session.get(API_URL + utility_operations.replace_spaces(alliance_name)) as response:
                    if response.status == 200:
                        try:
                            alliance_data = await response.json(content_type='text/plain')

                            process_alliance_data(alliance, alliance_data)

                        except json.JSONDecodeError as e:
                            print(f"Error decoding JSON response for alliance: {alliance_name} - {e}")
                            continue

                    else:
                        print(f"Failed to fetch data for alliance: {alliance_name} - Status Code: {response.status}")

    except Exception as e:
        print(f"Error checking alliances: {e}")