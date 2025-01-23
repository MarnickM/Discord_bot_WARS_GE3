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




@tasks.loop(minutes=1)
async def update_war_ready():
    global war_ready
    ready = await utility_operations.loadJson(PATH + "war_ready.json")
    war_ready = ready["war_ready"]



@tasks.loop(seconds=10)
async def check_enemy_attacks():
    global online_players
    global war_ready
    if war_ready == True:
        war = await utility_operations.loadJson(PATH + WAR_INFO)
        alliance_name = war["name"]
        alliance_search = utility_operations.replace_spaces(alliance_name)
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(API_URL + alliance_search) as response:
                        if response.status == 200:
                            alliance_data = await response.json(content_type='text/plain')
                            members = alliance_data.get("Members", [])

                            try:
                                current_members = db_operations.get_enemy_players()
                            except Exception as e:
                                print(f"Error getting enemy players: {e}")
                            current_member_names = [doc['Name'] for doc in current_members]
                            # Remove players from online_players if they are no longer in the enemy alliance
                            for name in list(online_players.keys()):
                                if name not in current_member_names:
                                    online_players.pop(name, None)

                            for member in members:
                                member_name = member.get("Name", "")
                                try:
                                    player_data = db_operations.find_enemy_player(member_name)
                                except Exception as e:
                                    print(f"Error finding enemy player: {e}")
                                
                                if player_data:
                                    # Check if the player has more war points than the last time we checked
                                    # print(f"Player data: {member_name} - {player_data['total_warpoints']} - {member['TotalWarPoints']}")
                                    if player_data['total_warpoints'] != 0 and member['TotalWarPoints'] != 0:
                                        # print("We got here")
                                        
                                        if player_data['total_warpoints'] < member['TotalWarPoints']:
                                            # print(f"case 1 for {member_name}")
                                            online_players[member_name] = datetime.now()
                                        # If the player has 0 war points and has gained some
                                        elif player_data['total_warpoints'] == 0 and member['TotalWarPoints'] > player_data['initial_warpoints']:
                                            # print(f"case 2 for {member_name}")
                                            online_players[member_name] = datetime.now()
                                        # If the player has the same war points as the last time we checked
                                        elif player_data['total_warpoints'] == member['TotalWarPoints'] and player_data['initial_warpoints'] == player_data['total_warpoints']:
                                            if member_name in online_players:
                                                # Check if the player has been online for more than 15 minutes, if so he is now offline and must be removed
                                                if (datetime.now() - online_players[member_name]) > timedelta(minutes=15):
                                                    # print(f"case 3 for {member_name}")
                                                    online_players.pop(member_name, None)
                                             # Update the player's war points in the database
                                db_operations.update_enemy_player(member_name, member['TotalWarPoints'])

                            # print(online_players)
        except Exception as e:
            print(f"Error checking enemy attacks: {e}")

@tasks.loop(seconds=30)
async def get_online_status():
    global online_players
    global war_ready
    if war_ready == True:
         war = await utility_operations.loadJson(PATH + WAR_INFO)
         for player in war["members"]:
             status = await utility_operations.get_online_status(player)
             if status == 2:
                 online_players[player] = datetime.now()   



async def main():
    get_online_status.start()  # Start the periodic task
    check_enemy_attacks.start()
    update_war_ready.start()
    print("running")
    while True:
        await asyncio.sleep(3600)  # Keep the script running

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())