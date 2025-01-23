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
    check_players_top_alliances.start()  # Start the periodic task
    while True:
        await asyncio.sleep(3600)  # Keep the script running

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())




@tasks.loop(hours=12)
async def check_players_top_alliances():
         try:
             # Fetch top alliances
             async with aiohttp.ClientSession() as session:
                 async with session.get(API_LB) as response:
                     if response.status == 200:
                         alliances = await response.json(content_type="text/plain")
     
                         
                         for alliance in alliances:
                             alliance_name = alliance['Name']
                             
                             # Fetch detailed info for each alliance
                             async with session.get(f"{API_URL}{alliance_name}") as alliance_response:
                                 if alliance_response.status == 200:
                                     alliance_info = await alliance_response.json(content_type="text/plain")
                                     # Process alliance_info as needed
                                     members = alliance_info.get("Members", [])
                                     for member in members:
                                         member_name = member['Name']
                                         player_info = db_operations.get_afk(name=member_name)
                                         if player_info:
                                             if player_info['warpoints'] != member['TotalWarPoints']:
                                                 db_operations.update_afk(member_name, member['TotalWarPoints'])
                                         else:
                                             db_operations.create_afk(member_name, member['TotalWarPoints'])
     
                                 else:
                                     print(f"Failed to fetch details for alliance: {alliance_name}")

         except Exception as e:
            print(f"Error checking top alliances and players: {e}")