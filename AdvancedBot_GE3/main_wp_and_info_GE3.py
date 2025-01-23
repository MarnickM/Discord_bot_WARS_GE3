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
async def update_war_info_from_database():
    if war_ready == True:
         try:
             # Load current war_info.json
             war_info = await utility_operations.loadJson(PATH + WAR_INFO)
     
             # Get all members from war_info
             members = war_info.get("members", {})
             # print(f"Members: {members}")
     
             # Iterate over each member and update their colonies
             for member_name, colonies in members.items():
                 # Fetch player data from your database
                 player_data = db_operations.find_player(member_name)
     
                 if player_data:
                     # Clear existing colonies for the member
                     members[member_name] = {}
     
                     # Update colonies C0-C11
                     for i in range(0, 12):
                         colony_key = f"C{i}"
                         if colony_key in player_data and player_data[colony_key] and len(player_data[colony_key]) == 3:
                             members[member_name][colony_key] = player_data[colony_key]
     
             # Update war_info with modified members data
             war_info["members"] = members
     
             # Save updated war_info.json
             await utility_operations.saveJson(PATH + WAR_INFO, war_info)
             await utility_operations.get_sorted_players_by_sb_level(PATH + WAR_INFO)
     
         except Exception as e:
             print(f"Error updating war_info.json: {e}")

    else:
        current_time = datetime.now() - timedelta(hours=8)
        current_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
        
        war = await utility_operations.loadJson(PATH + WAR_INFO)
        try:
            
            for player, player_data in war["members"].items():
                for planet, planet_data in player_data.items():
                    if planet_data[0] == "unknown":
                        
                        # Find player data in the database
                        db_player_data = db_operations.find_player(player)
                        if db_player_data:
                            colony = planet
                            current_data = db_player_data[colony]
                            
                            # Update the downtime
                            new_data = [current_time, current_data[1], current_data[2]]
                            
                            # Update the database
                            db_operations.update_colony(player, colony, new_data)
        
        except FileNotFoundError:
            print(f"Error: The file {PATH + WAR_INFO} was not found.")
        except json.JSONDecodeError:
            print("Error: JSON decoding error.")
        except KeyError as e:
            print(f"Error: Missing key in data structure - {e}")
        except Exception as e:
            print(f"Error removing unknowns: {e}")
    







@tasks.loop(seconds=20)
async def refresh_main_wp():
    try:
        global points
        points = 0
        global warpoints
        main_wp = await utility_operations.loadJson(PATH + "points.json")
        # Fetch alliance data
        async with aiohttp.ClientSession() as session:
                    async with session.get("https://api.galaxylifegame.net/Alliances/get?name=Galactic%20EmpireIII") as alliance_response:
                        alliance_data = await alliance_response.json(content_type='text/plain')
        
        if alliance_response.status == 200:
            members = alliance_data.get("Members", [])
            for member in members:
                member_id = member["Id"]
                
                # Fetch player data using member_id
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"https://api.galaxylifegame.net/Users/get?id={member_id}") as player_response:
                         if player_response.status == 200:

                             player_data = await player_response.json(content_type='text/plain')
                             planets = player_data.get("Planets", [])
                             
                             if planets:
                                 first_planet_hq_level = planets[0].get("HQLevel", 0)
                                #  wp = warpoints.get(first_planet_hq_level, 0)
                                #  points += wp
                                 points += first_planet_hq_level
                             else:
                                 print(f"No planets found for player ID {member_id}")
                         else:
                             print(f"Failed to fetch player data for ID {member_id} - Status Code: {player_response.status}")
        
        else:
            print(f"Failed to fetch alliance data - Status Code: {alliance_response.status}")
       
        main_wp["points"] = points
        await utility_operations.saveJson(PATH + "points.json", main_wp)
    
    except Exception as e:
        print(f"Error in refresh_main_wp function: {e}")



async def main():
    refresh_main_wp.start()  # Start the periodic task
    update_war_info_from_database.start()
    update_war_ready.start()
    print("running")
    while True:
        await asyncio.sleep(3600)  # Keep the script running

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())