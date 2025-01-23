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
import re

load_dotenv()

# class files imports
from database import database
from utility import utility_commands
from dropdown import dropdown
from database_Alex import database_Alex
from button import button
# from database_Alex import database_Alex

# define class variables
db_operations = database.DatabaseConnection()
utility_operations = utility_commands.utilityOperations()
db_Alex = database_Alex.DatabaseConnection()

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
CHANNEL_ID_COORDS = 1323700737502482513
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

global split_needed
split_needed = True
global number_of_splits
number_of_splits = 1

global embed_coords
embed_coords = ''
global embed_status
embed_status = ''
global embed_alliance
embed_alliance = ''

# ID's
garyID = 781062676557594625
evoID = 196032505940279296
juiceID = 351204529229922305


# set up the bot
bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())

@bot.event
async def on_ready():
    print('Bot is ready')
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands")
        # check_war_status.start()
        # find_top_5_least_downtime.start()
        # update_war_ready.start()
        info.start()
        # send_player_dropdowns.start()
            #  refresh_main_wp.start()
            #  check_alliances.start()
            #  update_war_info_from_database.start()
            #  update_players_our_alliance.start()
            #  get_online_status.start()
            #  check_enemy_attacks.start()
            #  check_players_top_alliances.start()
            #  info.start()
    except Exception as e:
        print(f"Failed to sync commands: {e}")
    # await reset_message_id()
    # await reset_dropdown_messages()
    # await reset_message_id_coords()
    # await reset_message_id_coords_groups()

# sync commands
@bot.command()
async def sync(ctx) -> None:
  guild = bot.get_guild(1072190344835387392)
  synced = await bot.tree.sync(guild=guild)
  print(f"Synced {len(synced)} commands.")



@tasks.loop(minutes=1)
async def update_war_ready():
    global war_ready
    ready = await utility_operations.loadJson(PATH + "war_ready.json")
    war_ready = ready["war_ready"]






async def reset_message_id():
    message = await utility_operations.loadJson(PATH + "message_id_overview.json")
    guild = bot.get_guild(GUILD_ID)
    if guild:
        channel = guild.get_channel(CHANNEL_ID)
        if channel:
            message_id = message["id"]
            if message_id:
                try:
                    message_in_channel = await channel.fetch_message(message_id)
                    if message_in_channel:
                        await message_in_channel.delete()
                    message["id"] = 0
                except Exception as e:
                    message["id"] = 0
    await utility_operations.saveJson(PATH + "message_id_overview.json", message)



async def reset_dropdown_messages():
    # Load the message IDs from the JSON file
    message_ids = await utility_operations.loadJson(PATH + "war_dropdown_ids.json")
    
    guild = bot.get_guild(GUILD_ID)
    if guild:
        channel = guild.get_channel(CHANNEL_ID)
        if channel:
            if message_ids and message_ids["ids"]:
                for message_id in message_ids["ids"]:
                    try:
                        # Attempt to fetch the message by ID
                        message_in_channel = await channel.fetch_message(message_id)
                        if message_in_channel:
                            await message_in_channel.delete()  # Delete the message
                            print(f"Deleted message ID {message_id}")
                    except discord.errors.NotFound:
                        print(f"Message with ID {message_id} not found; it may have already been deleted.")
                    except Exception as e:
                        print(f"Error deleting message ID {message_id}: {e}")

                # Clear the IDs since all messages have been deleted
                message_ids["ids"] = []
                await utility_operations.saveJson(PATH + "war_dropdown_ids.json", message_ids)
                print("Cleared dropdown message IDs.")



# async def reset_message_id_coords():
#     message = await utility_operations.loadJson(PATH + "coords_message.json")
#     guild = bot.get_guild(GUILD_ID)
#     if guild:
#         channel = guild.get_channel(CHANNEL_ID_COORDS)
#         if channel:
#             message_id = message["id"]
#             if message_id:
#                 try:
#                     message_in_channel = await channel.fetch_message(message_id)
#                     if message_in_channel:
#                         await message_in_channel.delete()
#                     message["id"] = 0
#                 except Exception as e:
#                     message["id"] = 0
#     await utility_operations.saveJson(PATH + "coords_message.json", message)





# async def reset_message_id_coords_groups():
#     for i in range(1,5):
#         message = await utility_operations.loadJson(f"{PATH}coords_message_group_{i}.json")
#         guild = bot.get_guild(GUILD_ID)
#         if guild:
#             channel = guild.get_channel(CHANNEL_ID_COORDS)
#             if channel:
#                 message_id = message["id"]
#                 if message_id:
#                     try:
#                         message_in_channel = await channel.fetch_message(message_id)
#                         if message_in_channel:
#                             await message_in_channel.delete()
#                         message["id"] = 0
#                     except Exception as e:
#                         message["id"] = 0
#         await utility_operations.saveJson(f"{PATH}coords_message_group_{i}.json", message)




async def time_suggestion(interaction: discord.Interaction, time: int) -> typing.List[app_commands.Choice[int]]:
    suggestions = [app_commands.Choice(name=str(i), value=i) for i in range(3, 8)]
    return suggestions

# @bot.tree.command(name="set_time", description="set a custom rebuild time for the war")
# @app_commands.autocomplete(time=time_suggestion)
# @app_commands.describe(time="The time in hours")
# async def set_time(interaction: discord.Interaction, time: int):
#     global regentime
#     if type(time) != int:
#         await interaction.response.send_message("The time must be an integer")
#         return
#     if time < 3:
#         await interaction.response.send_message("The rebuild time cannot be less than 3 hours")
#         return
#     if time > 7:
#         await interaction.response.send_message("The rebuild time cannot be more than 7 hours")
#         return
#     regentime = time
#     await interaction.response.send_message(f"Rebuild time set to {time} hours")

















@tasks.loop(seconds=30)
async def find_top_5_least_downtime():
    try:
        war = await utility_operations.loadJson(PATH + WAR_INFO)
        global top_5_least_downtime
        
        # List to store all planets with their downtimes
        temp_sorting = []
        
        # tempTime = war["members"][member][planet][0]
        # tempTime = datetime.strptime(tempTime, "%Y-%m-%d %H:%M:%S")

        # timeDifference = currentTime - tempTime
        # # added the actualRegenTime instead of the hard coded 3h time
        # if timeDifference >= timedelta(hours=actualRegenTime):
        
        for player, player_data in war["members"].items():
            for planet, planet_data in player_data.items():
                downtime_str = planet_data[0]
                if downtime_str != "unknown":
                    if downtime_str != "0":
                        downtime = downtime_str
                    else:
                        # Set downtime to a large past value if it's "0"
                        downtime = (datetime.now() - timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")
                    
                    temp_sorting.append((player, planet, downtime))
        
        # Sort planets by downtime (furthest from now to nearest)
        temp_sorting.sort(key=lambda x: x[2], reverse=True)
        # print("Sorted:")
        # for i in temp_sorting:
        #     print(i)
        
        # Select the top 5 planets
        top_5_temp = temp_sorting[-5:]
        # print(top_5_temp)
        top_5_least_downtime = {player: [planet, downtime] for player, planet, downtime in top_5_temp}
        # print("Formatted:")
        # print(top_5_least_downtime)
    
    except FileNotFoundError:
        print(f"Error: The file {PATH + WAR_INFO} was not found.")
    except json.JSONDecodeError:
        print("Error: JSON decoding error.")
    except Exception as e:
        print(f"Error finding top 5 least downtime: {e}")


async def format_top_5_least_downtime():
    try:
        main_wp = await utility_operations.loadJson(PATH + "points.json")
        points = main_wp["points"]
        
        war = await utility_operations.loadJson(PATH + WAR_INFO)
        
        if points != 0:
            Enemy_SB_sum = 0
            for player, player_data in war["members"].items():
                if "C0" in player_data:
                    sb_value = int(player_data["C0"][2][2:])
                    Enemy_SB_sum += sb_value
            
            rebuildTime = utility_operations.get_regenTime(us=points, enemy=Enemy_SB_sum)
            
            currentTime = datetime.now()
            formatted_data = ""
            
            for player, (colony, downtime) in top_5_least_downtime.items():
                if downtime != "0":
                    downtime = datetime.strptime(downtime, "%Y-%m-%d %H:%M:%S")
                    
                    timeDifference = currentTime - downtime
                    timeLeft = timedelta(hours=rebuildTime) - timeDifference
                    hoursLeft = timeLeft.seconds // 3600
                    minutesLeft = (timeLeft.seconds % 3600) // 60
                    
                    # Check if calculated downtime exceeds rebuild time
                    if timeDifference > timedelta(hours=rebuildTime):
                        if colony == "C0":
                            formatted_data += f":white_check_mark: {player}: main - UP\n"
                        else:
                            formatted_data += f":white_check_mark: {player}: {colony} - UP\n"
                    else:
                        formatted_data += f":octagonal_sign: {player}: {colony} - {hoursLeft}h:{minutesLeft}m\n"
                
                else:
                    if colony == "C0":
                        formatted_data += f":white_check_mark: {player}: main - UP\n"
                    else:
                        formatted_data += f":white_check_mark: {player}: {colony} - UP\n"

            formatted_data = re.sub(r"\bC0\b", "main", formatted_data)
            return formatted_data
        
        else:
            return "Booting up...."
    
    except FileNotFoundError:
        print(f"Error: The file {PATH + WAR_INFO} or points.json was not found.")
    except json.JSONDecodeError:
        print("Error: JSON decoding error.")
    except Exception as e:
        print(f"Error formatting top 5 least downtime: {e}")

















async def alliance_suggestion(interaction: discord.Interaction, alliance_name: str) -> typing.List[app_commands.Choice[str]]:
    players = db_operations.get_alliances(alliance_name)
    suggestions = [app_commands.Choice(name=name, value=name) for name in players]
    return suggestions
    

async def add_new_alliance(alliance_name):
    async with aiohttp.ClientSession() as session:
            async with session.get(API_URL + utility_operations.replace_spaces(alliance_name)) as response:
                if response.status == 200:
                    await db_operations.add_alliance(alliance_name)
    
# @bot.tree.command(name="createwar", description="Create a new war")
# @app_commands.autocomplete(alliance=alliance_suggestion)
# @app_commands.checks.has_any_role(General_role_id, Captain_role_id)
# @app_commands.describe(alliance="Name of the enemy alliance")
# async def createwar(interaction: discord.Interaction, alliance: str):
#     await interaction.response.defer() # Defer the response to avoid timeout
#     await asyncio.sleep(1.5)  # Sleep for 1 second to avoid
    
#     global war_ready
#     if db_operations.get_alliances(alliance) == []:
#        async with aiohttp.ClientSession() as session:
#             async with session.get(API_URL + utility_operations.replace_spaces(alliance)) as response:
#                 if response.status == 200:
#                     alliance = response.get("Name","")
#                     await db_operations.add_alliance(alliance)
#                     await interaction.followup.send(f"The alliance '{alliance}' was not in the database yet, it is now added")
#                 else:
#                     await interaction.followup.send(f"The alliance '{alliance}' doesn't seem to exist or you mistyped it")
#                     return
    
#     global regentime
#     regentime = 0

#     war = await utility_operations.loadJson(PATH + WAR_INFO)
#     if war["name"] == alliance:
#         await interaction.followup.send(f"War against {alliance} has already been created")
#         return

#     await db_operations.initiate_enemy_players(alliance)
#     war_ready = True
#     ready = await utility_operations.loadJson(PATH + "war_ready.json")
#     ready["war_ready"] = True
#     await utility_operations.saveJson(PATH + "war_ready.json", ready)

#     try:
#         # Fetch data for the enemy alliance
#         async with aiohttp.ClientSession() as session:
#             async with session.get(API_URL + utility_operations.replace_spaces(alliance)) as response:
#                 if response.status == 200:
#                     enemy_alliance_data = await response.json(content_type='text/plain')
#                     members = enemy_alliance_data.get("Members", [])
#                     members.sort(key=lambda x: x.get("Level", ""))

#                     war_members = {}
#                     for member in members:
#                         player_name = member.get("Name", "")
#                         player_id = member.get("Id", "")

#                         # Fetch player details from your database
#                         player_data = db_operations.find_player(player_name)
#                         if player_data is None:
#                             # If player_data is None, create a new player entry
#                             player_data = {"Alliance": "Alliance name", "Name": player_name, "id": player_id}
#                             player_data["C0"] = []

#                             # Fetch player info from API to get main planet's starbase level
#                             async with session.get(API_ID + player_id) as player_response:
#                                 if player_response.status == 200:
#                                     player_info = await player_response.json(content_type='text/plain')
#                                     planets = player_info.get("Planets", [])
#                                     if planets:
#                                         main_planet_hq_level = planets[0].get("HQLevel", "")
#                                         player_data["C0"].append((datetime.now() - timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S"))
#                                         player_data["C0"].append("0")
#                                         player_data["C0"].append(f"SB{main_planet_hq_level}")
#                                     else:
#                                         player_data["C0"] = []

#                                     # Add empty colonies C1-C11
#                                     for i in range(1, 12):
#                                         player_data[f"C{i}"] = []

#                                     # Add player to database
#                                     insert_result = db_operations.add_player(player_data)
#                                     if not insert_result:
#                                         raise Exception(f"Failed to add player {player_name} to the database")

#                         # Extract filled coordinates for the player
#                         player_coordinates = {}
#                         for i in range(0, 12):  # Iterate over C1 to C11
#                             colony_key = f"C{i}"
#                             if colony_key in player_data and player_data[colony_key] and len(player_data[colony_key]) == 3:
#                                 player_coordinates[colony_key] = player_data[colony_key]
                            
#                         # Add player coordinates to war_members
#                         war_members[player_name] = player_coordinates

#                     # Update war information with enemy alliance details
#                     war["name"] = alliance
#                     war["members"] = war_members

#                     # Save updated war_info.json
#                     await utility_operations.saveJson(PATH + WAR_INFO, war)
#                     # await utility_operations.get_sorted_players_by_sb_level(PATH + WAR_INFO)

#                     await interaction.followup.send(f"War has been created against {alliance}")

#                 else:
#                     await interaction.followup.send(f"Failed to fetch data for enemy alliance - Status Code: {response.status}")

#     except Exception as e:
#         await interaction.followup.send(f"Error creating war: {e}")


# @createwar.error
# async def createwar_error(interaction: discord.Interaction, error):
#     await interaction.response.send_message(f"You do not have the required permissions to create a war: {error}")










# @bot.tree.command(name="war_ready", description="(Gary only) Re-enable auto update for war info in case of bot restart")
# @app_commands.checks.has_role(General_role_id)
# async def war_ready(interaction: discord.Interaction):
#     global war_ready
#     war_ready = True
#     ready = await utility_operations.loadJson(PATH + "war_ready.json")
#     ready["war_ready"] = True
#     await utility_operations.saveJson(PATH + "war_ready.json", ready)
#     await interaction.response.send_message("War_ready set to True", ephemeral=True)

# @war_ready.error
# async def war_ready_error(interaction: discord.Interaction, error):
#     await interaction.response.send_message(f"You do not have the required role to use this command.", ephemeral=True)





    









# @bot.tree.command(name="info", description="Get all the enemy planets")
# async def info(interaction: discord.Interaction):
#   await interaction.response.defer()
#   await asyncio.sleep(2)
#   war = await utility_operations.loadJson(PATH + WAR_INFO)
#   main_wp = await utility_operations.loadJson(PATH + "points.json")
#   points = main_wp["points"]
  
# #   await utility_operations.get_sorted_players_by_sb_level(PATH + WAR_INFO)
  
#   EnemyAlliance_wp_sum = 0
#   Enemy_SB_sum = 0
#   EnemyAlliance_total_wp_sum = 0


#   for player, player_data in war["members"].items():
#     if "C0" in player_data:
#       sb_value = int(player_data["C0"][2][2:])
#       EnemyAlliance_wp_sum += warpoints.get(sb_value, 0)
#       Enemy_SB_sum += sb_value

#   for player, player_data in war["members"].items():
#     for planet, planet_data in player_data.items():
#         sb_value = int(planet_data[2][2:])
#         EnemyAlliance_total_wp_sum += warpoints.get(sb_value, 0)

#   actualRegenTime = utility_operations.get_regenTime(us=points, enemy=Enemy_SB_sum)
#   enemyRegenTime = utility_operations.get_regenTime(us=Enemy_SB_sum, enemy=points)
#   global regentime
#   if regentime != 0:
#     actualRegenTime = regentime
  
#   embed = discord.Embed(
#       title=war["name"],
#       description=
#       f"WP main {EnemyAlliance_wp_sum} / total WP {EnemyAlliance_total_wp_sum}",
#       color=discord.Colour.from_rgb(0,0,0))
#   currentTime = datetime.now()

# #   claim = await utility_operations.loadJson("./claim.json")

#   global info_data 
#   info_data = actualRegenTime

#   if len(war["members"]) <= 25:
#     for member in war["members"]:
#       text = ""
#       for planet in war["members"][member]:

#         # checking if time is unknown
#         if war["members"][member][planet][0] == "unknown":
#             starbaselvl = war["members"][member][planet][2]
#             if planet== "C0":
#               text += f":warning: main {starbaselvl}-> ????\n"
#               continue
#             else:
#               coords = war["members"][member][planet][1]
#               text += f":warning: {planet} {coords} {starbaselvl}-> ????\n"
#               continue

#         if war["members"][member][planet][0] == "0":
#           # get the starbase lvl from position 2
#           starbaselvl = war["members"][member][planet][2]
#           if planet == "C0":

#             # check for claims
#             # claimed = False
#             # for key,value in claim["members"].items():
#             #    if member == value[2] and value[0] == "claimed" and value[3] == "C0":
#             #       text += f":lock: main  {starbaselvl}-> UP\n"
#             #       claimed = True
#             # if claimed == False:
#             text += f":white_check_mark: main  {starbaselvl}-> UP\n"

#           else:
#             coords = war["members"][member][planet][1]
#             # for key,value in claim["members"].items():
#             #    if war["members"][member] == value[2] and value[0] == "claimed" and value[3] == planet:
#             #       text += f":lock: {planet} {coords} {starbaselvl}-> UP\n"
#             #       claimed = True

#             # if claimed == False:
#             text += f":white_check_mark: {planet} {coords} {starbaselvl}-> UP\n"
#           continue

#         tempTime = war["members"][member][planet][0]
#         tempTime = datetime.strptime(tempTime, "%Y-%m-%d %H:%M:%S")

#         timeDifference = currentTime - tempTime
#         # added the actualRegenTime instead of the hard coded 3h time
#         if timeDifference >= timedelta(hours=actualRegenTime):
#           war["members"][member][planet][0] = "0"
#           # get the starbase lvl from position 2
#           starbaselvl = war["members"][member][planet][2]

#           if planet == "C0":
#             # claimed = False
#             # for key,value in claim["members"].items():
#             #    if war["members"][member] == value[2] and value[0] == "claimed" and value[3] == "C0":
#             #       text += f":lock: main  {starbaselvl}-> UP\n"
#             #       claimed = True

#             # if claimed == False:
#             text += f":white_check_mark: main {starbaselvl}-> UP\n"
#           else:
#             starbaselvl = war["members"][member][planet][2]
#             coords = war["members"][member][planet][1]
#             # claimed = False
#             # for key,value in claim["members"].items():
#             #    if war["members"][member] == value[2] and value[0] == "claimed" and value[3] == planet:
#             #       text += f":lock: {planet} {coords} {starbaselvl}-> UP\n"
#             #       claimed = True

#             # if claimed == False:
#             text += f":white_check_mark: {planet} {coords} {starbaselvl}-> UP\n"
#         else:
#           # added the actualRegenTime instead of the hard coded 3h time
#           timeLeft = timedelta(hours=actualRegenTime) - timeDifference
#           hoursLeft = timeLeft.seconds // 3600
#           minutesLeft = (timeLeft.seconds % 3600) // 60

#           ptemp = ":octagonal_sign: " + planet
#           coords = war["members"][member][planet][1]
#           # get the starbase lvl from position 2
#           starbaselvl = war["members"][member][planet][2]


#           if planet == "C0":

#             # claimed = False
#             # for key,value in claim["members"].items():
#             #     if war["members"][member] == value[2] and value[0] == "claimed" and value[3] == "C0":
#             #       ptemp = ":lock: main"
#             #       coords = ""
#             #       claimed = True

#             # if claimed == False:
#               ptemp = ":octagonal_sign: main"
#               coords = ""
          
#         #   for key,value in claim["members"].items():
#         #       if war["members"][member] == value[2] and value[0] == "claimed" and value[3] == planet:
#         #         ptemp = ":lock:" + planet

#           # added starbaselvl in the display
#           text += f"{ptemp} {coords} {starbaselvl}-> {hoursLeft}h:{minutesLeft}m\n"

#       embed.add_field(name=member, value=text, inline=True)

#     embed.set_footer(text=f"Rebuild time: {actualRegenTime} / Enemy rebuild time: {enemyRegenTime}")
#     await utility_operations.saveJson(PATH + WAR_INFO, war)
#     await interaction.followup.send(embed=embed)

#   else:
#     max_members_per_embed = 25

#     # Calculate the total number of members
#     total_members = len(war["members"])

#     # Iterate over members in chunks of max_members_per_embed
#     for start_index in range(0, total_members, max_members_per_embed):
#       end_index = start_index + max_members_per_embed
#       current_members = list(war["members"].items())[start_index:end_index]

#       embed = discord.Embed(
#           title=war["name"],
#           description=
#           f"WP main {EnemyAlliance_wp_sum} / total WP {EnemyAlliance_total_wp_sum}",
#           color=discord.Colour.from_rgb(0,0,0))

#       for member, member_data in current_members:
#         text = ""
#         for planet in member_data:

#             # checking if time is unknown
#           if war["members"][member][planet][0] == "unknown":
#               starbaselvl = war["members"][member][planet][2]
#               if planet== "C0":
#                 text += f":warning: main {starbaselvl}-> ????\n"
#                 continue
#               else:
#                 coords = war["members"][member][planet][1]
#                 text += f":warning: {planet} {coords} {starbaselvl}-> ????\n"
#                 continue

#           if war["members"][member][planet][0] == "0":
#             # get the starbase lvl from position 2
#             starbaselvl = war["members"][member][planet][2]
#             if planet == "C0":
#               text += f":white_check_mark: main  {starbaselvl}-> UP\n"
#             else:
#               coords = war["members"][member][planet][1]
#               text += f":white_check_mark: {planet} {coords} {starbaselvl}-> UP\n"
#             continue

#           tempTime = war["members"][member][planet][0]
#           tempTime = datetime.strptime(tempTime, "%Y-%m-%d %H:%M:%S")

#           timeDifference = currentTime - tempTime
#           # added the actualRegenTime instead of the hard coded 3h time
#           if timeDifference >= timedelta(hours=actualRegenTime):
#             war["members"][member][planet][0] = "0"
#             # get the starbase lvl from position 2
#             starbaselvl = war["members"][member][planet][2]
#             if planet == "C0":
#               text += f":white_check_mark: main {starbaselvl}-> UP\n"
#             else:
#               coords = war["members"][member][planet][1]
#               # get the starbase lvl from position 2
#               starbaselvl = war["members"][member][planet][2]
#               # added the starbaselvl in the display
#               text += f":white_check_mark: {planet} {coords} {starbaselvl}-> UP\n"
#           else:
#             # added the actualRegenTime instead of the hard coded 3h time
#             timeLeft = timedelta(hours=actualRegenTime) - timeDifference
#             hoursLeft = timeLeft.seconds // 3600
#             minutesLeft = (timeLeft.seconds % 3600) // 60

#             ptemp = ":octagonal_sign: " + planet
#             coords = war["members"][member][planet][1]
#             # get the starbase lvl from position 2
#             starbaselvl = war["members"][member][planet][2]
#             if planet == "C0":
#               ptemp = ":octagonal_sign: main"
#               coords = ""

#             # added starbaselvl in the display
#             text += f"{ptemp} {coords} {starbaselvl}-> {hoursLeft}h:{minutesLeft}m\n"

#         embed.add_field(name=member, value=text, inline=True)

#       embed.set_footer(text=f"Rebuild time: {actualRegenTime} / Enemy rebuild time: {enemyRegenTime}")
#       await utility_operations.saveJson(PATH + WAR_INFO, war)
#       await interaction.followup.send(embed=embed)













    
# @bot.tree.command(name="status", description="Give status of top 50 alliances")
# async def status(interaction: discord.Interaction):
#     await interaction.response.send_message("Please be patient... gathering info")
#     async with aiohttp.ClientSession() as session:
#                     async with session.get("https://api.galaxylifegame.net/Alliances/warpointLb") as response:
#                         alliance_data = await response.json(content_type="text/plain")[:50]  # Fetch only the first 50 alliances

#     total_alliances = len(alliance_data)
#     num_batches = (total_alliances + 24) // 25  # Calculate the number of batches

#     for batch in range(num_batches):
#         start_index = batch * 25
#         end_index = min(start_index + 25, total_alliances)

#         embed = discord.Embed(title=f"Status of top 50 alliances - Part {batch + 1}",
#                               color=discord.Colour.from_rgb(255, 191, 0))
#         for i in range(start_index, end_index):
#             text = ""
#             alliance = alliance_data[i]
#             alliance_search = utility_operations.replace_spaces(alliance["Name"])
#             async with aiohttp.ClientSession() as session:
#                     async with session.get(f"https://api.galaxylifegame.net/Alliances/get?name={alliance_search}") as response:
#                         alliance_info = await response.json(content_type="text/plain")

#             if alliance_info["InWar"]:
#                 alliance_search = utility_operations.replace_spaces(alliance_info["OpponentAllianceId"])
#                 async with aiohttp.ClientSession() as session:
#                     async with session.get(f"https://api.galaxylifegame.net/Alliances/get?name={alliance_search}") as opponents:
#                         enemy_alliance_data = await opponents.json(content_type="text/plain")
#                 text += f"in war with {enemy_alliance_data['Name']}"
#             else:
#                 text += "not in war"

#             embed.add_field(name=f"#{i + 1} {alliance_info['Name']}", value=text)

#         await interaction.followup.send(embed=embed)




















async def player_suggestion(interaction: discord.Interaction, player_name: str) -> typing.List[app_commands.Choice[str]]:
    players = db_operations.get_players(player_name)
    suggestions = [app_commands.Choice(name=name, value=name) for name in players]
    return suggestions

# @bot.tree.command(name="addcolony", description="Add a new colony")
# @app_commands.autocomplete(name=player_suggestion)
# @app_commands.describe(name="Player name", colony="Colony number", coordinates="Coordinates", sb="Starbase level")
# async def addcolony(interaction: discord.Interaction, name: str, colony: int, coordinates: str, sb: int):
#     await interaction.response.defer() # Defer the response to avoid timeout
#     await asyncio.sleep(2)  # Sleep for 1 second to avoid
    
#     # Get current date and time
#     current_time = datetime.now()
#     current_time -= timedelta(hours=8)
#     current_time = current_time.strftime("%Y-%m-%d %H:%M:%S")

#     # Check if the player exists
#     existing_player = db_operations.find_player(name)
#     if existing_player:
#         colony_data = [current_time, coordinates, f"SB{sb}"]
#         colony_num = f"C{colony}"
        
#         # Check if colony_num already exists in player's data
#         if colony_num in existing_player:
#             # Clear existing colony data (if needed)
#             existing_player[colony_num] = []  # Replace with empty list to clear data
        
#         # Add or update colony data
#         existing_player[colony_num] = colony_data
        
#         # Update the player's data in the database
#         update_result = db_operations.update_colony(name=name, colony_num=colony_num, colony_data=colony_data)
    
#         if update_result:
#             await interaction.followup.send(f"Updated colony data for {name}: {colony_num} - {coordinates} - SB{sb}")
#         else:
#             await interaction.followup.send(f"Failed to update colony data for {name}")
#     else:
#         # Player does not exist, create a new player entry with basic layout
#         player_data = {"Alliance": "Alliance name", "Name": name, "id": ""}
#         colony_data = [current_time, coordinates, f"SB{sb}"]
#         colony_num = f"C{colony}"
        
#         downtime = current_time
#         war_info = await utility_operations.loadJson(PATH + WAR_INFO)
#         if name in war_info["members"]:
#             downtime = war_info["members"][name]["C0"][0]
#             if downtime == "0":
#                 downtime = current_time

#         async with aiohttp.ClientSession() as session:
#             async with session.get(API_NAME + name) as response:
#                 if response.status == 200:
#                     player_info = await response.json(content_type='text/plain')
#                     planets = player_info.get("Planets", [])
#                     if planets:
#                         main_planet_hq_level = planets[0].get("HQLevel", "")
#                         player_data["C0"] = [downtime, "0", f"SB{main_planet_hq_level}"]
#                 else:
#                     print(f"Failed to fetch player data for {name} - Status Code: {response.status}")
#                     await interaction.followup.send('This player does not exist in the game, did you type it correctly? :eyes:')
#                     return
        
#         # Add empty colonies C1-C11
#         for i in range(1, 12):
#             player_data[f"C{i}"] = []
        
#         # Add the new colony data
#         player_data[colony_num] = colony_data
        
#         insert_result = db_operations.add_player(player_data)
#         if insert_result:
#             await interaction.followup.send(f"Added new player {name} with {colony_data[1]} and {colony_data[2]}")
#         else:
#             await interaction.followup.send(f"Failed to add new player {name}")



# @addcolony.error
# async def addcolony_error(interaction: discord.Interaction, error):
#     await interaction.response.send_message(f"An error occurred: {error}")



# @bot.tree.command(name="multi_addcolony", description="Add multiple colonies for a single player (respect the order of input)")
# @app_commands.autocomplete(name=player_suggestion)
# @app_commands.describe(name="Player name", colonies="Colony numbers separated by ;", coordinates="Coordinates separated by ;", sb="Starbase levels separated by ;")
# async def multi_addcolony(interaction: discord.Interaction, name: str, colonies: str, coordinates: str, sb: str):
#     await interaction.response.defer()  # Defer the response to avoid timeout
#     await asyncio.sleep(3)  # Sleep for 1 second to avoid

#     multiple_colonies = ';' in colonies and ';' in coordinates and ';' in sb

#     # Parse input strings
#     if multiple_colonies:
#        colony_numbers = colonies.split(';')
#        coordinates_list = coordinates.split(';')
#        starbases = sb.split(';')
#     else:
#         await interaction.followup.send("You are missing a **;** in your input.")

#     # Ensure the lengths match
#     if not (len(colony_numbers) == len(coordinates_list) == len(starbases)):
#         await interaction.followup.send("The number of colonies, coordinates, and starbase levels must match.")
#         return

#     # Get current date and time
#     current_time = datetime.now()
#     current_time -= timedelta(hours=8)
#     current_time = current_time.strftime("%Y-%m-%d %H:%M:%S")

#     # Check if the player exists
#     existing_player = db_operations.find_player(name)
#     if not existing_player:
#         # Player does not exist, create a new player entry with basic layout
#         player_data = {"Alliance": "Alliance name", "Name": name, "id": ""}
#         # Ensure C0 is always added first
#         player_data["C0"] = []
#         # Add empty colonies C1-C11
#         for i in range(1, 12):
#             player_data[f"C{i}"] = []
        
#         async with aiohttp.ClientSession() as session:
#             async with session.get(API_NAME + name) as response:
#                 if response.status == 200:
#                     player_info = await response.json(content_type='text/plain')
#                     planets = player_info.get("Planets", [])
#                     if planets:
#                         main_planet_hq_level = planets[0].get("HQLevel", "")
#                         player_data["C0"] = [current_time, "0", f"SB{main_planet_hq_level}"]
#                 else:
#                     print(f"Failed to fetch player data for {name} - Status Code: {response.status}")
#                     await interaction.followup.send('This player does not exist in the game, did you type it correctly? :eyes:')
#                     return

#     results = []

#     # Loop through the colonies, coordinates, and starbases
#     for colony, coordinate, starbase in zip(colony_numbers, coordinates_list, starbases):
#         colony_num = f"C{colony}"
#         if int(colony) < 1 or int(colony) > 11:
#             results.append(f"Invalid colony number: {colony} for {name}")
#             continue
#         colony_data = [current_time, coordinate, f"SB{starbase}"]

#         if existing_player:
#             # Update existing player
#             if colony_num in existing_player:
#                 # Clear existing colony data (if needed)
#                 existing_player[colony_num] = []  # Replace with empty list to clear data

#             # Add or update colony data
#             existing_player[colony_num] = colony_data

#             # Update the player's data in the database
#             update_result = db_operations.update_colony(name=name, colony_num=colony_num, colony_data=colony_data)
#             if update_result:
#                 results.append(f"Updated colony {colony_num} for {name}: {coordinate} - SB{starbase}")
#             else:
#                 results.append(f"Failed to update colony {colony_num} for {name}")
#         else:
#             # Add the new colony data for the new player
#             player_data[colony_num] = colony_data

#     if not existing_player:
#         # Insert new player into the database
#         insert_result = db_operations.add_player(player_data)
#         if insert_result:
#             results.append(f"Added new player {name} with colonies: " + ", ".join([f"{player_data[col][1]} - {player_data[col][2]}" for col in player_data if col.startswith('C') and player_data[col]]))
#         else:
#             results.append(f"Failed to add new player {name}")

#     await interaction.followup.send("\n".join(results))







        










# async def player_war_suggestion(interaction: discord.Interaction, player_name: str) -> typing.List[app_commands.Choice[str]]:
#     players = await db_operations.get_players_from_json(player_name)
#     suggestions = [app_commands.Choice(name=name, value=name) for name in players]
#     return suggestions

# @bot.tree.command(name="delcolony", description="Delete a colony")
# @app_commands.autocomplete(name=player_war_suggestion)
# @app_commands.describe(name="Player name", colony="Colony number")
# async def delcolony(interaction: discord.Interaction, name: str, colony: int):
#     # Check if the player exists
#     existing_player = db_operations.find_player(name)
    
#     if existing_player:
#         colony_num = f"C{colony}"
        
#         # Check if colony_num exists in player's data
#         if colony_num in existing_player:
#             # Update the colony field to an empty array
#             existing_player[colony_num] = []
            
#             # Update the player's data in the database
#             update_result = db_operations.update_colony(name=name, colony_num=colony_num, colony_data=[])
            
#             if update_result:
#                 await interaction.response.send_message(f"Deleted {colony_num} for {name}")
#             else:
#                 await interaction.response.send_message(f"Failed to delete colony for {name}")
#         else:
#             await interaction.response.send_message(f"{colony_num} does not exist for {name}")
#     else:
#         await interaction.response.send_message(f"Player {name} does not exist")













# @bot.tree.command(name="unknown", description="Set the down time of an enemy to unknown")
# @app_commands.describe(name="Player name", colony="Colony number")
# @app_commands.autocomplete(name=player_war_suggestion)
# async def unknown(interaction: discord.Interaction, name: str, colony: str = "0"):
#       await interaction.response.defer()
#       await asyncio.sleep(2)
#       war = await utility_operations.loadJson(PATH + WAR_INFO)
#       if colony != "0":
#         if int(colony) < 1 or int(colony) > 11:
#           await interaction.followup.send("There can only be colonies between 1 and 11")
#           return
    
#       ctemp = "C" + colony

#       existing_player = db_operations.find_player(name)
#       if existing_player:
#            colony_num = f"C{colony}"
#            current_data = []
#            current_time = "unknown"
           
#            # Check if colony_num already exists in player's data
#            if colony_num in existing_player:
#                # check if it is empty
#                if existing_player[colony_num] == []:
#                    await interaction.followup.send(f"{interaction.user.mention} {colony_num} of {name} doesn't exist")
#                    return
#                current_data = existing_player[colony_num]
#                # Clear existing colony data (if needed)
#                existing_player[colony_num] = []  # Replace with empty list to clear data
           
#            # only change the time
#            colony_data = [current_time, current_data[1], current_data[2]]
#            # Add or update colony data
#            existing_player[colony_num] = colony_data
           
#            # Update the player's data in the database
#            update_result = db_operations.update_colony(name=name, colony_num=colony_num, colony_data=colony_data)
       
#            if update_result:
#                if colony == "0":
#                    await interaction.followup.send(f"**{name}** **main** down time unkown")
#                else:
#                    await interaction.followup.send(f"**{name}** **{ctemp}** down time unknown")
#            else:
#                await interaction.followup.send(f"Failed to set {colony_num} downtime unknown for {name}")
#       elif existing_player is None:
#            await interaction.followup.send(f"{interaction.user.mention} Player {name} does not exist")







# @bot.tree.command(name="registered_scores", description="Show the registered scores via the /down command")
# async def registered_scores(interaction: discord.Interaction):
#     members = db_operations.get_all_members_GE2()  # Fetch all members
#     total_score_actual = 0
#     total_score_gained = 0
#     for member in members:
#          actual_score = member["actual_score"]
#          total_score_actual += actual_score
#          points_gained = member["points_gained"]
#          total_score_gained += points_gained

#     embed = discord.Embed(title="Registered Scores", description=f"**Score via /down VS in game score**\n **Total: {total_score_actual}** <:Warpoints:1265337329577492676> - **{total_score_gained}** <:Warpoints:1265337329577492676>", color=discord.Color.blue())
#     members = db_operations.get_all_members_GE2() 
#     # To store formatted player name and score pairs
#     player_lines = []
    
#     # Iterate over the cursor and format the player data
#     for member in members:
#         player_name = member["Name"]
#         actual_score = member["actual_score"]
#         points_gained = member["points_gained"]
#         player_lines.append(f"**{actual_score}** <:Warpoints:1265337329577492676> VS **{points_gained}** <:Warpoints:1265337329577492676> for {player_name}")

#     # Add fields to the embed with 5 players per field
#     for i in range(0, len(player_lines), 5):
#         chunk = player_lines[i:i+5]
#         # Players {i+1}-{i+len(chunk)} for setting player 1-5 in titles
#         embed.add_field(name=f"-------------------", value="\n".join(chunk), inline=False)
#     embed.set_footer(text="Note: this does not take into account the score reductions/bonuses from attacking with a 2+ higher/lower SB level")
    
#     # Send the embed in response to the command
#     await interaction.response.send_message(embed=embed)








# @bot.tree.command(name="down", description="Mark an enemy as destroyed")
# @app_commands.autocomplete(name=player_war_suggestion)
# @app_commands.describe(name="Player name", colony="Colony number")
# async def down(interaction: discord.Interaction, name: str, colony: int = 0):
#     await interaction.response.defer() # Defer the response to avoid timeout
#     await asyncio.sleep(2)  # Sleep for 1 second to avoid

#     if (colony < 1 or colony > 11) and colony != 0:
#         await interaction.followup.send("Colony number must be between 1 and 11")
#         return
#     if type(colony) != int:
#         await interaction.followup.send("Colony number must be an integer")
#         return
    
#     global warpoints
#     current_score = 0
#     # Get current date and time
#     current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#     game_name = interaction.user.display_name
#     player_data = db_operations.find_player_GE2(game_name)
#     # print(player_data)

#     # Check if the player exists
#     existing_player = db_operations.find_player(name)
#     if existing_player:

#         colony_num = f"C{colony}"
#         current_data = []
        
#         # Check if colony_num already exists in player's data
#         if colony_num in existing_player:
#             # check if it is empty
#             if existing_player[colony_num] == []:
#                 await interaction.followup.send(f"{interaction.user.mention} {colony_num} of {name} doesn't exist")
#                 return
#             current_data = existing_player[colony_num]
#             # print(current_data)
#             sb_level = current_data[2]
#             sb_number = int(sb_level[2:])
#             score = warpoints.get(sb_number, 0)
#             # rint(score)
            
#             if player_data is not None:
#                 current_score = player_data["actual_score"]
#                 current_score += score
#                 player_data["actual_score"] = current_score
#                 # print(player_data)
#                 db_operations.update_player_GE2(game_name, player_data)

#             # Clear existing colony data (if needed)
#             existing_player[colony_num] = []  # Replace with empty list to clear data
        
#         # only change the time
#         colony_data = [current_time, current_data[1], current_data[2]]
#         # Add or update colony data
#         existing_player[colony_num] = colony_data
        
#         # Update the player's data in the database
#         update_result = db_operations.update_colony(name=name, colony_num=colony_num, colony_data=colony_data)
    
#         if update_result:
#             if colony == 0:
#                 await interaction.followup.send(f"Main down of {name}")
#             else:
#                 await interaction.followup.send(f"{colony_num} down of {name}")
#         else:
#             await interaction.followup.send(f"Failed to down {colony_num} of {name}")
#     elif existing_player is None:
#         await interaction.followup.send(f"{interaction.user.mention} Player {name} does not exist")













# @bot.tree.command(name="up", description="Mark an enemy as rebuild")
# @app_commands.autocomplete(name=player_war_suggestion)
# @app_commands.describe(name="Player name", colony="Colony number")
# async def up(interaction: discord.Interaction, name: str, colony: int = 0):
#     await interaction.response.defer() # Defer the response to avoid timeout
#     await asyncio.sleep(2)  # Sleep for 1 second to avoid
    
#     if (colony < 1 or colony > 11) and colony != 0:
#         await interaction.followup.send("Colony number must be between 1 and 11")
#         return
#     if type(colony) != int:
#         await interaction.followup.send("Colony number must be an integer")
#         return
    
#     # Get current date and time
#     current_time = datetime.now()
#     current_time -= timedelta(hours=8)
#     current_time = current_time.strftime("%Y-%m-%d %H:%M:%S")

#     # Check if the player exists
#     existing_player = db_operations.find_player(name)
#     if existing_player:

#         colony_num = f"C{colony}"
#         current_data = []
        
#         # Check if colony_num already exists in player's data
#         if colony_num in existing_player:
#             # check if it is empty
#             if existing_player[colony_num] == []:
#                 await interaction.followup.send(f"{interaction.user.mention} {colony_num} of {name} doesn't exist")
#                 return
#             current_data = existing_player[colony_num]
#             # Clear existing colony data (if needed)
#             existing_player[colony_num] = []  # Replace with empty list to clear data
        
#         # only change the time
#         colony_data = [current_time, current_data[1], current_data[2]]
#         # Add or update colony data
#         existing_player[colony_num] = colony_data
        
#         # Update the player's data in the database
#         update_result = db_operations.update_colony(name=name, colony_num=colony_num, colony_data=colony_data)
    
#         if update_result:
#             if colony == 0:
#                 await interaction.followup.send(f"Main up of {name}")
#             else:
#                 await interaction.followup.send(f"{colony_num} up of {name}")
#         else:
#             await interaction.followup.send(f"Failed to up {colony_num} of {name}")
#     elif existing_player is None:
#         await interaction.followup.send(f"{interaction.user.mention} Player {name} does not exist")
















# @bot.tree.command(name="war", description="Get the current war status")
# @app_commands.autocomplete(alliance_name=alliance_suggestion)
# @app_commands.describe(alliance_name="Name of the alliance")
# async def war(interaction: discord.Interaction, alliance_name: str):
#     try:
#         # Fetch data for the user's alliance
#         alliance_search = utility_operations.replace_spaces(alliance_name)
#         async with aiohttp.ClientSession() as session:
#             async with session.get(API_URL + alliance_search) as response:

#                  if response.status == 200:
#                      alliance_data = await response.json(content_type="text/plain")
#                      in_war = alliance_data.get("InWar", False)
#                      if in_war:
#                          enemy_alliance_id = alliance_data.get("OpponentAllianceId", "Unknown")
         
#                          # Fetch data for the enemy alliance
#                          async with aiohttp.ClientSession() as session:
#                                 async with session.get(API_URL + utility_operations.replace_spaces(enemy_alliance_id)) as enemy_alliance_response:
#                                    if enemy_alliance_response.status == 200:
#                                         enemy_alliance_data = await enemy_alliance_response.json(content_type="text/plain")
#                                         enemy_alliance_name = enemy_alliance_data.get("Name", "Unknown")
                   
#                                         our_score = await db_operations.get_score(alliance_name)
#                                         our_score_formatted = utility_operations.format_score(our_score)

#                                         their_score = await db_operations.get_score(enemy_alliance_name)
#                                         their_score_formatted = utility_operations.format_score(their_score)

#                                         war_start_time = db_operations.get_war_start_time(alliance_name)

#                                         # get time until 3 day end mark
#                                         if war_start_time != "*not tracked*":
#                                            current_time = datetime.now()
#                                            three_day_mark = war_start_time + timedelta(days=3)
#                                            max_duration_left = three_day_mark - current_time
                                                   
#                                            # Format max duration left as HH:MM:SS
#                                            max_duration_hours = max_duration_left.total_seconds() // 3600
#                                            max_duration_minutes = (max_duration_left.total_seconds() % 3600) // 60
#                                            max_duration_seconds = max_duration_left.total_seconds() % 60
#                                            max_duration_str = f"{int(max_duration_hours)}:{int(max_duration_minutes):02}:{int(max_duration_seconds):02}"
   
                      
#                                            # Calculate remaining time if available
#                                         #    fifteen_hour_mark = war_start_time + timedelta(hours=14) + timedelta(minutes=10)
                                                       
#                                                        # Calculate remaining time based on the score
#                                            remaining_time = db_operations.calculate_remaining_time(our_score, their_score, war_start_time)
#                                         #    if remainingTime == "no points yet":
#                                         #            # Set remainingTime to the 15-hour mark if no points yet
#                                         #            remainingTime = fifteen_hour_mark.timestamp()
#                                         #    else:
#                                         #        # Convert remainingTime to a timedelta
#                                         #        remaining_time_delta = timedelta(seconds=remainingTime)
#                                         #        calculated_end_time = current_time + remaining_time_delta
                                                       
#                                         #        # Determine the appropriate end time
#                                         #    if current_time < fifteen_hour_mark:
#                                         #            remainingTime = fifteen_hour_mark.timestamp()
#                                         #    else:
#                                         #        remainingTime = calculated_end_time.timestamp()
                                                       
#                                         #    # Ensure remainingTime is an integer Unix timestamp
#                                         #    remaining_time = int(remainingTime)
#                                         else:
#                                             remaining_time = 1000000000
#                                             max_duration_str = "*not tracked*"
                      
#                                        # Construct embed with scores, progress bar, and remaining time
#                                         embed = discord.Embed(
#                                            title=f"{alliance_name} vs {enemy_alliance_name}",
#                                            color=discord.Color.red(),
#                                         )
                   
#                                         embed.add_field(name="", value=f"{our_score_formatted} <:Warpoints:1265337329577492676>    :    {their_score_formatted} <:Warpoints:1265337329577492676>", inline=False)
#                                         embed.add_field(name="Earliest KO", value=f"<t:{remaining_time}:R>", inline=False)
#                                         embed.add_field(name="Time left", value=max_duration_str, inline=False)
                   
#                                         await interaction.response.send_message(embed=embed)
#                                    else:
#                                         await interaction.response.send_message(f"Failed to fetch data for enemy alliance - Status Code: {enemy_alliance_response.status}")
#                      else:
#                          await interaction.response.send_message(f"Alliance {alliance_name} is not currently in a war.")
#                  else:
#                      await interaction.response.send_message(f"Failed to fetch data for alliance {alliance_name} - Status Code: {response.status}")
  
#     except json.JSONDecodeError as e:
#         if "Expecting value: line 1 column 1 (char 0)" in str(e):
#             await interaction.response.send_message("You mistyped the name, this alliance doesn't exist or I don't track the score of this alliance.")
#             # Handle the error, for example, by setting a default value
#         else:
#             # Print the exception message if it's a different JSONDecodeError
#             await interaction.response.send_message(f"Unexpected JSONDecodeError: {e}")
#             # Re-raise the exception
#             raise

#     except AttributeError as e:
#         if "'NoneType' object has no attribute 'get'" in str(e):
#             await interaction.response.send_message("You mistyped the name, this alliance doesn't exist or I don't track the score of this alliance.")
#             # Handle the error, for example, by setting a default value
#         else:
#             # Print the exception message if it's a different AttributeError
#             await interaction.response.send_message(f"Unexpected AttributeError: {e}")
#             # Re-raise the exception
#             raise




















global ping_captains
ping_captains = True
global war_status_sent
war_status_sent = False

@tasks.loop(minutes=1)
async def check_war_status():
    global online_players
    global war_ready
    global ping_captains
    global war_status_sent
    message_id = await utility_operations.loadJson(PATH + "message_id_overview.json")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://api.galaxylifegame.net/Alliances/get?name={utility_operations.replace_spaces(ALLIANCE_NAME)}") as response:

                     if response.status == 200:
                         alliance_data = await response.json(content_type="text/plain")
                         in_war = alliance_data.get("InWar", False)
             
                         guild = bot.get_guild(GUILD_ID)
                         if guild:
                             channel = guild.get_channel(CHANNEL_ID)
                             if channel:
                                 if in_war:
                                     global sum_for_war
                                     global sum_against_war
                                     ping_captains = True
                                     sum_for_war = 0
                                     sum_against_war = 0

                                     enemy_alliance_id = alliance_data.get("OpponentAllianceId", "Unknown")  # Get the name of the enemy alliance
             
                                     # Fetch enemy alliance details using the name to get the info
                                     async with aiohttp.ClientSession() as session:
                                            async with session.get(f"https://api.galaxylifegame.net/Alliances/get?name={utility_operations.replace_spaces(enemy_alliance_id)}") as enemy_alliance_response:
                                                if enemy_alliance_response.status == 200:
                                                    try:
                                                        enemy_alliance_data = await enemy_alliance_response.json(content_type="text/plain")
                                                        enemy_alliance_name = enemy_alliance_data.get("Name", "Unknown")
                                                        wins = enemy_alliance_data.get("WarsWon", 0)
                                                        losses = enemy_alliance_data.get("WarsLost", 0)
                                                        winrate = wins / (wins + losses) if wins + losses > 0 else 0
                        
                                                    except json.JSONDecodeError as json_error:
                                                        print(f"Error decoding JSON for enemy alliance: {json_error}")
                                                        enemy_alliance_name = "Unknown"
                                                else:
                                                    print(f"Failed to fetch enemy alliance data - Status Code: {enemy_alliance_response.status}")
                                                    enemy_alliance_name = "Unknown"
                        
                                                # Load war_info.json
                                                war_info = await utility_operations.loadJson(PATH + WAR_INFO)
                                                if war_info:
                                                    # Set regenTime to the global regentime variable
                                                    regenTime = regentime
                        
                                                    total_planets_count = 0
                                                    discovered_planets_count = 0
                                                    up_planets_count = 0
                                                    destroyed_planets_count = 0
                        
                                                    current_time = datetime.now()
                                                    regen_delta = timedelta(hours=regenTime)
                        
                                                    for member_name, member_info in war_info["members"].items():
                                                        for colony, colony_info in member_info.items():
                                                            total_planets_count += 1  # Count every colony for the total
                                                            if colony_info[0] != "0" and colony_info[0] != "unknown":
                                                                colony_time = datetime.strptime(colony_info[0], "%Y-%m-%d %H:%M:%S")
                                                                if current_time - colony_time > regen_delta:
                                                                    up_planets_count += 1  # Count every colony for destroyed planets
                                                            else:
                                                                pass
                                                            if colony != "C0":
                                                               discovered_planets_count += 1  # Only count non-C0 colonies for discovered planets
                                                    # destroyed_planets_count = total_planets_count - up_planets_count
                                                    destroyed_planets_count = total_planets_count - up_planets_count

                                                    # Calculate scores
                                                    our_score = await db_operations.get_score(ALLIANCE_NAME)
                                                    our_score_formatted = utility_operations.format_score(our_score)
                                                    their_score = await db_operations.get_score(enemy_alliance_name)
                                                    their_score_formatted = utility_operations.format_score(their_score)

                                                    # initiate war start
                                                    war_start_time = db_operations.get_war_start_time(ALLIANCE_NAME)

                                                    if war_start_time != "*not tracked*":
                                                          # get time until 3 day end mark
                                                          three_day_mark = war_start_time + timedelta(days=3)
                                                          max_duration_left = three_day_mark - current_time
                                                      
                                                          # Format max duration left as HH:MM:SS
                                                          max_duration_hours = max_duration_left.total_seconds() // 3600
                                                          max_duration_minutes = (max_duration_left.total_seconds() % 3600) // 60
                                                          max_duration_seconds = max_duration_left.total_seconds() % 60
                                                          max_duration_str = f"{int(max_duration_hours)}:{int(max_duration_minutes):02}:{int(max_duration_seconds):02}"
      
                                                          # Calculate remaining time based on the score
                                                          remaining_time = db_operations.calculate_remaining_time(our_score, their_score, war_start_time)

                                                    else:
                                                        remaining_time = 1000000000
                                                        max_duration_str = "*not tracked*"
                        
                                                    # Calculate progress bar
                                                    max_length = 14
                                                    if their_score > 0:
                                                        our_progress = int((our_score / (our_score + their_score)) * max_length)
                                                    else:
                                                        our_progress = max_length  # Fill up the bar entirely if their_score is 0
                                                    their_progress = max_length - our_progress
                                                    progress_bar = "▰" * our_progress + "▱" * their_progress
                        
                                                    # Construct embed with progress bar, scores, and enemy logo
                                                    embed = discord.Embed(
                                                        title=f"{enemy_alliance_name}",
                                                        description=progress_bar,
                                                        color=discord.Color.red(),
                                                        timestamp=datetime.now(timezone.utc)
                                                    )
                        
                                                    # Fetch enemy alliance logo URL based on emblem data
                                                    emblem_data = enemy_alliance_data.get("Emblem", {})
                                                    shape = emblem_data.get("Shape", 0)
                                                    pattern = emblem_data.get("Pattern", 0)
                                                    icon = emblem_data.get("Icon", 0)
                                                    enemy_logo_url = f"https://cdn.galaxylifegame.net/content/img/alliance_flag/AllianceLogos/flag_{shape}_{pattern}_{icon}.png"
                                                    embed.set_thumbnail(url=enemy_logo_url)
                        
                                                    # Add fields to embed
                                                    # invisible character to create space between fields \u1CBC\u1CBC
                                                    embed.add_field(name="", value=f"**{str(our_score_formatted)}** <:Warpoints:1265337329577492676> VS **{str(their_score_formatted)}** <:Warpoints:1265337329577492676>", inline=True)
                                                    embed.add_field(name="", value=f":stopwatch: KO: <t:{remaining_time}:R> \n:chart_with_upwards_trend: Winrate: {winrate:.2%} \n:ringed_planet: Discovered Colonies: {discovered_planets_count} \n:boom: Destroyed Planets: {destroyed_planets_count}/{total_planets_count}", inline=False)
                                                    embed.add_field(name="", value="-----------------------------------", inline=True)
                                                    
                                                    if online_players == {}:
                                                        embed.add_field(name=":no_entry: Online players", value="Nobody is online...", inline=False)
                                                    else:
                                                        text = ""
                                                        for player, timestamp in online_players.items():
                                                            if datetime.now() - timestamp < timedelta(minutes=15):
                                                                text += f"{player}\n"
                                                        if text == "":
                                                            text = "Nobody is online..."
                                                        embed.add_field(name=":no_entry: Online players", value=text, inline=False)
                                                    
                                                    embed.add_field(name=":hourglass: Time left", value=f"{max_duration_str}", inline=False)
                                                    embed.add_field(name="", value="-----------------------------------", inline=True)

                                                    upcoming_bases = await format_top_5_least_downtime()
                                                    embed.add_field(name="Upcoming bases", value=f"{upcoming_bases}", inline=False)
                        
                                                    # Give the ScoreDropDownView the members list
                                                    members = list(db_operations.get_all_members_GE2())
                                                    dropdown_view = dropdown.ScoreDropDownView(members)
                                                    
                                                    # Update or send the embed
                                                    if message_id["id"] != 0:
                                                        message = await channel.fetch_message(message_id["id"])
                                                        await message.edit(embed=embed,view=dropdown_view)
                                                        await message.clear_reaction("✅")
                                                        await message.clear_reaction("<:white_cross_mark:1264941666943373352>")
                                                    else:
                                                        message = await channel.send(embed=embed, view=dropdown_view)
                                                        message_id["id"] = message.id
                                                        await utility_operations.saveJson(PATH + "message_id_overview.json", message_id)
                        
                                                else:
                                                    print(f"Failed to load war_info.json")
                                                war_status_sent = True
                                 else:
                                     war_status_sent = False
                                     ready = await utility_operations.loadJson(PATH + "war_ready.json")
                                     ready["war_ready"] = False
                                     await utility_operations.saveJson(PATH + "war_ready.json", ready)
                                     embed = discord.Embed(
                                                        title=f"We are not at war",
                                                        color=discord.Color.red(),
                                                        timestamp=datetime.now(timezone.utc)
                                                    )
                                     embed.add_field(name="Who is ready for war?", value=":white_check_mark: / <:white_cross_mark:1264941666943373352>")
                                 
                                     if message_id["id"] != 0:
                                         message = await channel.fetch_message(message_id["id"])
                                         await message.edit(embed=embed, view=None)
                                         await message.add_reaction("✅")
                                         await message.add_reaction("<:white_cross_mark:1264941666943373352>")
                                         # <:red_cross:1072245059577196554>
                                     else:
                                        message = await channel.send(embed=embed, view=None)
                                        message_id["id"] = message.id
                                        await utility_operations.saveJson(PATH + "message_id_overview.json", message_id)
                     else:
                         print(f"Failed to fetch data for alliance: {ALLIANCE_NAME} - Status Code: {response.status}")
    except Exception as e:
        if isinstance(e, discord.errors.NotFound) and "404 Not Found (error code: 10008): Unknown Message" in str(e):
            print(f"regenerating message")
        else:
            print(f"Error checking war status: {e}")



global initialized
initialized = False
@tasks.loop(minutes=1)
async def initialize_war():

    global initialized
    if initialized == False:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://api.galaxylifegame.net/Alliances/get?name={utility_operations.replace_spaces(ALLIANCE_NAME)}") as response:
                if response.status == 200:
                    alliance_data = await response.json(content_type="text/plain")
                    in_war = alliance_data.get("InWar", False)
                    if in_war:
                        enemy_alliance_id = alliance_data.get("OpponentAllianceId", "Unknown")
                        async with aiohttp.ClientSession() as session:
                            async with session.get(f"https://api.galaxylifegame.net/Alliances/get?name={utility_operations.replace_spaces(enemy_alliance_id)}") as enemy_alliance_response:
                                if enemy_alliance_response.status == 200:
                                    try:
                                        enemy_alliance_data = await enemy_alliance_response.json(content_type="text/plain")
                                        enemy_players = enemy_alliance_data.get("Members", [])

                                        for player in enemy_players:
                                            player_name = player.get("Name", "Unknown")
                                            player_id = player.get("Id", "Unknown")
                                            async with aiohttp.ClientSession() as session:
                                                async with session.get(f"https://api.galaxylifegame.net/Users/get?id={player_id}") as player_response:
                                                    if player_response.status == 200:
                                                        try:
                                                            player_data = await player_response.json(content_type="text/plain")
                                                            colonies = player_data.get("Planets", [])
                                                            player_colonies = {
                                                                player_name: [colony.get("HQLevel", 0) for colony in colonies],
                                                                "level": player_data.get("Level", 0)
                                                            }

                                                        except json.JSONDecodeError as json_error:
                                                            print(f"Error decoding JSON for enemy player: {json_error}")
                                                            return


                                        db_operations.update_dashboard_players()

                                    except json.JSONDecodeError as json_error:
                                        print(f"Error decoding JSON for enemy alliance: {json_error}")
                                        return
                else:
                    print(f"Failed to fetch data for alliance in Initialization: {ALLIANCE_NAME} - Status Code: {response.status}")
    else:
        pass
        

@tasks.loop(minutes=1)
async def send_player_dropdowns():
    global war_status_sent  # Assuming this variable indicates whether the war embed has been sent
    print(f"War Status Sent: {war_status_sent}")  # Enhanced logging
    if war_status_sent:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://api.galaxylifegame.net/Alliances/get?name={utility_operations.replace_spaces(ALLIANCE_NAME)}") as response:
                if response.status == 200:
                    alliance_data = await response.json(content_type="text/plain")
                    in_war = alliance_data.get("InWar", False)

                    guild = bot.get_guild(GUILD_ID)
                    if guild:
                        channel = guild.get_channel(CHANNEL_ID)
                        if channel:
                            if in_war:
                                enemy_alliance_id = alliance_data.get("OpponentAllianceId", "Unknown")

                                # Fetch enemy alliance details
                                async with aiohttp.ClientSession() as session:
                                    async with session.get(f"https://api.galaxylifegame.net/Alliances/get?name={utility_operations.replace_spaces(enemy_alliance_id)}") as enemy_alliance_response:
                                        if enemy_alliance_response.status == 200:
                                            try:
                                                enemy_alliance_data = await enemy_alliance_response.json(content_type="text/plain")
                                                enemy_players = enemy_alliance_data.get("Members", [])
                                            except json.JSONDecodeError as json_error:
                                                print(f"Error decoding JSON for enemy alliance: {json_error}")
                                                return  # Stop execution if there is a JSON error
                                        else:
                                            print(f"Failed to fetch enemy alliance data - Status Code: {enemy_alliance_response.status}")
                                            return

                                # Calculate the number of messages needed
                                nb_message = len(enemy_players) // 5
                                if len(enemy_players) % 5 > 0:
                                    nb_message += 1

                                # Load existing IDs
                                dropdown_ids = await utility_operations.loadJson(PATH + "war_dropdown_ids.json") or {"ids": []}

                                # Prepare player and colony data for each batch of 5 players
                                for it in range(nb_message):
                                    await asyncio.sleep(0.875)  # Add a slight delay between messages

                                    # Batch enemy players for current message
                                    current_batch = enemy_players[(it * 5):(it * 5 + 5)]

                                    # Create dropdown views with the updated player and colony data
                                    dropdown_view = await create_dropdown_view(current_batch)

                                    try:
                                        if it < len(dropdown_ids["ids"]):
                                            # Try fetching the existing message
                                            message = await channel.fetch_message(dropdown_ids["ids"][it])
                                            await message.edit(view=dropdown_view)  # Update existing message
                                        else:
                                            # Send a new message with the dropdown view
                                            message = await channel.send(content=" ", embed=None, view=dropdown_view)
                                            dropdown_ids["ids"].append(message.id)  # Store the new message ID

                                    except Exception as e:
                                        if isinstance(e, discord.errors.NotFound) and "404 Not Found (error code: 10008): Unknown Message" in str(e):
                                            # If the message was not found, send a new message
                                            print(f"Message with ID {dropdown_ids['ids'][it]} not found, sending a new message.")
                                            message = await channel.send(content=" ", embed=None, view=dropdown_view)
                                            if it < len(dropdown_ids["ids"]):
                                                dropdown_ids["ids"][it] = message.id  # Update existing ID
                                            else:
                                                dropdown_ids["ids"].append(message.id)  # Append new ID
                                        else:
                                            print(f"Error sending dropdown message: {e}")

                                # Ensure dropdown_ids only contains the right number of message IDs
                                if len(dropdown_ids["ids"]) > nb_message:
                                    dropdown_ids["ids"] = dropdown_ids["ids"][:nb_message]  # Trim excess IDs

                                # Save the updated message IDs to war_dropdown_ids.json
                                await utility_operations.saveJson(PATH + "war_dropdown_ids.json", dropdown_ids)

                            else:
                                # If not in war, clear existing dropdown messages
                                dropdown_ids = await utility_operations.loadJson(PATH + "war_dropdown_ids.json")
                                if dropdown_ids and dropdown_ids["ids"]:
                                    for message_id in dropdown_ids["ids"]:
                                        try:
                                            message = await channel.fetch_message(message_id)
                                            await message.delete()  # Delete the existing message
                                            print(f"Deleted message ID {message_id}")
                                        except discord.errors.NotFound:
                                            print(f"Message with ID {message_id} not found, it may have already been deleted.")

                                    # Clear the IDs since there are no messages
                                    dropdown_ids["ids"] = []
                                    await utility_operations.saveJson(PATH + "war_dropdown_ids.json", dropdown_ids)




async def create_dropdown_view(players):
    dropdown_view = ""
    for player in players:
        # Retrieve player colony data from database
        player_data = db_operations.find_dashboard_player(player['Name'])

        if player_data is not None:
            # Create and add the dropdown for this player
            # dropdown_contents = dropdown.ColonyDropDown(player_data)
            dropdown_view = dropdown.ColonyDropDownView(player_data)
        else:
            print('Player data not found for', player['Name'], 'while looking in dashboard')

    return dropdown_view





                                   





# async def update_claim():
#     claim = await utility_operations.loadJson(PATH + "claims.json")

#     members = db_operations.get_all_members_GE2()
#     member_names = [member["Name"] for member in members]
#     for name in member_names:
#         if name not in claim["members"]:
#             claim["members"][name] = {1: [], 2: [], 3: []}

#     await utility_operations.saveJson(PATH + "claims.json", claim)














# @bot.tree.command(name="claim", description="Claim a base for you to attack")
# @app_commands.autocomplete(name=player_war_suggestion)
# @app_commands.describe(name="Player name", colony="Colony number")
# async def claim(interaction: discord.Interaction, name: str, colony: int = 0):
#     # try: 

#              user = interaction.user.name
#              colony_str = f"C{colony}"
                 
#              if (colony < 1 or colony > 11) and colony != 0:
#                  await interaction.response.send_message("Colony number must be between 1 and 11")
#                  return
         
#              claim = await utility_operations.loadJson(PATH + "claims.json")
#              print(claim)
#              war = await utility_operations.loadJson(PATH + "war_info.json")
         
#              # Check if the specified player exists in the war info
#              if name not in war["members"]:
#                  await interaction.response.send_message(f"{name} does not exist")
#                  return
         
#              # Check if the colony exists for the player in war info
#              if colony_str not in war["members"][name]:
#                  await interaction.response.send_message(f"{colony_str} does not exist for {name}")
#                  return
         
#              current_time = datetime.now()
         
#              # Ensure the member exists in the claim.json file
#              if user not in claim["members"]:
#                  claim["members"][user] = {1: [], 2: [], 3: []}
#                  await utility_operations.saveJson(PATH + "claims.json", claim)

#             # check if someone hasn't already claimed the base
#              for member, slots in claim["members"].items():
#                 for slot, data in slots.items():
#                     if data:
#                         claim_time = datetime.fromisoformat(claim["members"][user][str(slot)][2])
#                         time_left = timedelta(minutes=15) - (current_time - claim_time)

#                         if data[1] == colony_str and data[0] == name and time_left.total_seconds() > 0:
#                             if colony != 0:
#                                 await interaction.response.send_message(f"{colony_str} of {name} is already claimed and has not expired yet (by {member})")
#                             else:
#                                 await interaction.response.send_message(f"Main of {name} is already claimed and has not expired yet (by {member})")
#                             return
         
#              claim = await utility_operations.loadJson(PATH + "claims.json")
#              # Check for an empty slot
#              for slot in range(1, 4):
#                  if not claim["members"][user][str(slot)]:
#                      claim["members"][user][str(slot)] = [name, colony_str, current_time]
#                      await utility_operations.saveJson(PATH + "claims.json", claim)
#                      if colony != 0:
#                         await interaction.response.send_message(f"{colony_str} of {name} claimed in slot {slot} for {user}")
#                      else:
#                         await interaction.response.send_message(f"Main of {name} claimed in slot {slot} for {user}")
#                      return
                 
#              counter_1 = 0
#              lowest_time = 0
#              claim_time = datetime.fromisoformat(claim["members"][user][str(1)][2])
#              time_left = timedelta(minutes=15) - (current_time - claim_time)
#              lowest_time = time_left
#              # All slots are filled, check if any can be overwritten
#              for slot in range(1, 4):
#                  claim_time = datetime.fromisoformat(claim["members"][user][str(slot)][2])
#                  time_left = timedelta(minutes=15) - (current_time - claim_time)
#                  if time_left < lowest_time:
#                     lowest_time = time_left

#                  if time_left.total_seconds() > 0:
#                      counter_1 += 1
#                  else:
#                      claim["members"][user][str(slot)] = [name, colony_str, current_time.isoformat()]
#                      await utility_operations.saveJson(PATH + "claims.json", claim)
#                      if colony != 0:
#                          await interaction.response.send_message(f"{colony_str} of {name} claimed in slot {slot} for {user}")
#                      else:
#                          await interaction.response.send_message(f"Main of {name} claimed in slot {slot} for {user}")
#                      return
         
#              if counter_1 == 3:
#                  lowest_time_str = f"{lowest_time.seconds // 60}m {lowest_time.seconds % 60}s"
#                  await interaction.response.send_message(f"You used your 3 claims and your cooldown is still active: **{lowest_time_str}** remaining.")
             
#     # except Exception as e:
#     #     print(f"Error claiming base: {e}")










async def fetch_embed_coords(name, Avatar):
          global embed_coords
          # 2nd page
          embed_coords = discord.Embed(title=f"Colony Data of {name}", color=discord.Color.from_rgb(255, 191, 0))
      
          player_data = db_operations.find_player(name)
          async with aiohttp.ClientSession() as session:
              async with session.get(API_NAME + name) as response:
                  if response.status == 200:
                      player_info = await response.json(content_type='text/plain')
                      planets = player_info.get("Planets", [])
                      levels = [planet.get("HQLevel", "") for planet in planets]
      
                      for i, level in enumerate(levels):
                          if i == 0:
                              embed_coords.add_field(name="Main Planet", value=f"SB{level}", inline=False)
                          else:
                              colony_index = f"C{i}"
                              if player_data:
                                  colony_data = player_data.get(colony_index, [])
                                  if colony_data:
                                      coordinates = colony_data[1]
                                      embed_coords.add_field(name=colony_index, value=f"SB{level} - :ringed_planet:  {coordinates}", inline=False)
                                  else:
                                      embed_coords.add_field(name=colony_index, value=f"SB{level} - :ringed_planet: ???", inline=False)
                              else:
                                  embed_coords.add_field(name=colony_index, value=f"SB{level} - :ringed_planet: ???", inline=False)
                  else:
                     print(f" Page 2: Failed to fetch data for player: {name} - Status Code: {response.status}")
          embed_coords.set_thumbnail(url=Avatar)

          return embed_coords





async def fetch_embed_status(name, Avatar):
          global embed_status
          # 3rd page
          embed_status = discord.Embed(title=f"Status of {name}", color=discord.Color.from_rgb(255, 191, 0))
          player_status = db_operations.get_afk(name)
          last_update = ''
          warpoints = 0
          alliance_id = ''
          alliance_name = ''
          now = datetime.now()
          if player_status:
              last_update = player_status['last_update']
              last_update = (last_update - now).days
      
              if last_update <= 0:
                  last_update = "Less than a day ago"
              elif last_update == 1:
                  last_update = "1 day ago"
              else:
                  last_update = f"{last_update} days ago"
      
              warpoints = player_status['warpoints']
              async with aiohttp.ClientSession() as session:
                  async with session.get(API_NAME + name) as response:
                      if response.status == 200:
                          player_data = await response.json(content_type="text/plain")
                          alliance_id = player_data.get("AllianceId", "")
                          if alliance_id != None and alliance_id != "":
                              async with session.get(API_URL + utility_operations.replace_spaces(alliance_id)) as alliance_response:
                                  if alliance_response.status == 200:
                                      alliance_data = await alliance_response.json(content_type="text/plain")
                                      alliance_name = alliance_data.get("Name", "")
                                  else:
                                      print(f"Failed to fetch data for player: {name} - Status Code: {response.status}")
                          else:
                              alliance_name = "User is not in an alliance"
                      else:
                          print(f"Page 3: Failed to fetch data for player: {name} - Status Code: {response.status}")
          else:
              last_update = "*This player is not being tracked...*"
              warpoints = "*This player is not being tracked...*"
              async with aiohttp.ClientSession() as session:
                  async with session.get(API_NAME + name) as response:
                      if response.status == 200:
                          player_data = await response.json(content_type="text/plain")
                          alliance_id = player_data.get("AllianceId", "")
                          if alliance_id != None and alliance_id != "":
                              async with session.get(API_URL + utility_operations.replace_spaces(alliance_id)) as alliance_response:
                                  if alliance_response.status == 200:
                                      alliance_data = await alliance_response.json(content_type="text/plain")
                                      alliance_name = alliance_data.get("Name", "")
                                  else:
                                      print(f"Failed to fetch data for player: {name} - Status Code: {response.status}")
                          else:
                              alliance_name = "User is not in an alliance"
                      else:
                          print(f"Page 3: Failed to fetch data for player: {name} - Status Code: {response.status}")
              
          embed_status.add_field(name="Alliance", value=alliance_name, inline=False)
          if type(warpoints) == int:
            embed_status.add_field(name="Warpoints", value=f"{utility_operations.format_number(warpoints)} <:Warpoints:1265337329577492676>", inline=False)
          else:
            embed_status.add_field(name="Warpoints", value=warpoints, inline=False)
          embed_status.add_field(name="Last played", value=last_update, inline=False)
          embed_status.set_thumbnail(url=Avatar)

          return embed_status








async def fetch_embed_alliance(alliance_name):
          global embed_alliance
          # 4th page
          colony_text = ''
          alliance_data_coords = ''
          if alliance_name != None:
              async with aiohttp.ClientSession() as session:
                  async with session.get(API_URL + utility_operations.replace_spaces(alliance_name)) as alliance_coords:
                      if alliance_coords.status == 200:
                          alliance_data_coords = await alliance_coords.json(content_type="text/plain")
                          members = alliance_data_coords.get("Members", [])
                          if len(members) < 25:
                              embed_alliance = discord.Embed(title=f"Coords of {alliance_name}", color=discord.Color.from_rgb(138, 43, 226))
                              for member in members:
                                  member_name = member["Name"]
                                  member_data = db_operations.find_player(member_name)
                                  colony_text = ""
                                  if member_data:
                                      for colony in range(1, 12):
                                          colony_num = f"C{colony}"
                                          if colony_num in member_data and colony_num != []:
                                              colony_data = member_data[colony_num]
                                              if colony_data:
                                                  coordinates = colony_data[1]
                                                  SB_level = colony_data[2]
                                                  colony_text += f"{colony_num} / {coordinates} / SB{SB_level}\n"
                                  embed_alliance.add_field(name=member_name, value=colony_text, inline=True)
                          else:
                                   columns = 3  # Number of columns
                                   embed_alliance = discord.Embed(title=f"Coords of {alliance_name}", color=discord.Color.from_rgb(138, 43, 226))
                                   
                                   # Group members into fields
                                   fields = [""] * columns
                                   for i, member in enumerate(members):
                                       field_index = i % columns
                                       member_name = member["Name"]
                                       member_data = db_operations.find_player(member_name)
                                       colony_text = ""
                                       if member_data:
                                           for colony in range(1, 12):
                                               colony_num = f"C{colony}"
                                               if colony_num in member_data and member_data[colony_num] != []:
                                                   colony_data = member_data[colony_num]
                                                   if colony_data:
                                                       coordinates = colony_data[1]
                                                       SB_level = colony_data[2]
                                                       colony_text += f"{colony_num} / {coordinates} / {SB_level}\n"
                                       
                                       fields[field_index] += f"**{member_name}**\n{colony_text}\n"
                                   
                                   # Add fields to embed
                                   for i, field in enumerate(fields):
                                       if field.strip():  # Only add non-empty fields
                                           embed_alliance.add_field(name="", value=field, inline=True)
                                 
                      else:
                          print(f"Page 4: Failed to fetch data for alliance: {alliance_name} - Status Code: {alliance_coords.status}")
          else:
                embed_alliance = discord.Embed(title=f"This user is not in an alliance", color=discord.Color.from_rgb(138, 43, 226))

          return embed_alliance









# @bot.tree.command(name="player_profile", description="Get the profile of a player")
# @app_commands.autocomplete(name=player_suggestion)
# @app_commands.describe(name="Player name")
# async def player_profile(interaction: discord.Interaction, name: str):
#     await interaction.response.defer()
#     asyncio.sleep(0.5)
#     try:
#           # 1st page
#           player_id = 0
#           Avatar = ""
#           attacks = 0
#           coloniesMoved = 0
#           nukesUsed = 0
#           coinsSpent = 0
#           buildingsDestroyed = 0
#           xpFromAttacks = 0
#           alliance_name = ""
#           async with aiohttp.ClientSession() as session:
#               async with session.get(API_NAME + name) as response:
#                   if response.status == 200:
#                       player_data = await response.json(content_type="text/plain")
#                       player_id = player_data.get("Id", 0)
#                       alliance_name = player_data.get("AllianceId", "User is not in an alliance")
#                       Avatar = player_data.get("Avatar", "")
#                       async with session.get(API_STATS + player_id) as personal_response:
#                               if personal_response.status == 200:
#                                   player_info = await personal_response.json(content_type="text/plain")
#                                   attacks = player_info.get("PlayersAttacked", 0)
#                                   coloniesMoved = player_info.get("ColoniesMoved", 0)
#                                   nukesUsed = player_info.get("NukesUsed", 0)
#                                   coinsSpent = player_info.get("CoinsSpent", 0)
#                                   buildingsDestroyed = player_info.get("BuildingsDestroyed", 0)
#                                   xpFromAttacks = player_info.get("ScoreFromAttacks", 0)
#                               else:
#                                   await interaction.followup.send(f"Failed to fetch data for player: {name} - Status Code: {response.status}")
          
#                   else:
#                       await interaction.followup.send(f"Page 1: Failed to fetch data for player: {name} - Status Code: {response.status}")
          
      
#           embed_profile = discord.Embed(title=f"Profile of {name}", color=discord.Color.from_rgb(255, 191, 0))
#           embed_profile.set_thumbnail(url=Avatar)
#           embed_profile.add_field(name="Players attacked", value=f"<:colossus:1265659546710577162> {utility_operations.format_number(attacks)}", inline=False)
#           embed_profile.add_field(name="Colonies moved", value=f":ringed_planet: {utility_operations.format_number(coloniesMoved)}", inline=True)
#           embed_profile.add_field(name="Nukes used", value=f"<:nuke:1265659594030452756> {utility_operations.format_number(nukesUsed)}", inline=False)
#           embed_profile.add_field(name="Coins spent", value=f"<:coins:1265659731440304170> {utility_operations.format_number(coinsSpent)}", inline=True)
#           embed_profile.add_field(name="Buildings destroyed", value=f"<:Compact_House:1265659617820676247> {utility_operations.format_number(buildingsDestroyed)}", inline=False)
#           embed_profile.add_field(name="XP from attacks", value=f"<:Experience:1265659691896143892> {utility_operations.format_number(xpFromAttacks)}", inline=True)
      
#           embed_coords, embed_status, embed_alliance = await asyncio.gather(
#                 fetch_embed_coords(name, Avatar),
#                 fetch_embed_status(name, Avatar),
#                 fetch_embed_alliance(alliance_name)
#           )  
#           pages = [embed_profile, embed_coords, embed_status, embed_alliance]
      
#           await interaction.followup.send(embed=pages[0], view=button.buttonMenu(pages, player_id))
        
#     except Exception as e:
#           await interaction.followup.send(f"Error fetching player profile: {e}")








# global split_needed
# split_needed = True

# @tasks.loop(minutes=1)
# async def info():
#     global split_needed
#     try:
#         GE2_data = db_operations.find_opponent_GE2()
#         if GE2_data:
#             enemy = GE2_data["OpponentAllianceId"]
#             if enemy != "":
#                 async with aiohttp.ClientSession() as session:
#                     async with session.get(API_URL + utility_operations.replace_spaces(enemy)) as response:
#                         if response.status == 200:
#                             enemy_data = await response.json(content_type="text/plain")
#                             enemy_name = enemy_data.get("Name", "Unknown")
#                             enemy_members = enemy_data.get("Members", [])
                            
#                             if not split_needed:
#                                 columns = 3  # Number of columns for the embed
#                                 embed_alliance = discord.Embed(title=f"Coordinates of {enemy_name}", color=discord.Color.from_rgb(255, 191, 0),timestamp=datetime.now(timezone.utc))
#                                 fields = [""] * columns

#                                 for idx, member in enumerate(enemy_members):
#                                     member_name = member['Name']
#                                     member_id = member['Id']
#                                     colonies = db_Alex.get_colonies(member_id)
#                                     found_colonies = db_Alex.found_colonies(member_id)

#                                     colony_info = f"**{member_name}**\n"
#                                     main_planet = db_Alex.get_player(member_id)
#                                     unix_time = utility_operations.get_unix_time(main_planet["MB_refresh_time"])
#                                     if main_planet['MB_status'] == "Up":
#                                         colony_info += f":white_check_mark: main SB{main_planet['MB_lvl']}\n"
#                                     else: 
#                                         colony_info += f":octagonal_sign: main SB{main_planet['MB_lvl']} - <t:{unix_time}:R>\n"

#                                     for colony in colonies:
#                                         coordinates = f"{colony['colo_coord']['x']},{colony['colo_coord']['y']}"
#                                         if coordinates != "-1,-1":
#                                              colony_number = f"C{colony['number']}"
#                                              SB_level = f"SB{colony['colo_lvl']}"

#                                              unix_time = utility_operations.get_unix_time(colony["colo_refresh_time"])

#                                              if colony['colo_status'] == "Up":
#                                                  colony_info += f":white_check_mark: {colony_number} - {SB_level} - {coordinates}\n"
#                                              elif colony['colo_status'] == "Down":
#                                                  colony_info += f":octagonal_sign: {colony_number} - {SB_level} - {coordinates} - <t:{unix_time}:R>\n"
#                                              else:
#                                                  colony_info += f":warning: {colony_number} - {SB_level} - {coordinates}\n"
                                    
#                                     for found_colony in found_colonies:
#                                         coordinates = f"{found_colony['X']},{found_colony['Y']}"
#                                         colony_info += f":grey_question: {coordinates}\n"

#                                     field_index = idx % columns
#                                     fields[field_index] += f"{colony_info}\n"
                                
#                                 for i, field in enumerate(fields):
#                                     if field.strip():  # Only add non-empty fields
#                                         embed_alliance.add_field(name="", value=field, inline=True)
                                
#                                 embed_alliance.set_footer(text="Last updated")
                                
#                                 members = list(db_operations.get_all_members_GE2())
#                                 dropdown_view = dropdown.ScoreDropDownView(members)
#                                 guild = bot.get_guild(GUILD_ID)
#                                 if guild:
#                                     channel = guild.get_channel(CHANNEL_ID_COORDS)
#                                     if channel:
#                                         message_id = await utility_operations.loadJson(PATH + "coords_message.json")
#                                         if message_id["id"] != 0:
#                                             message = await channel.fetch_message(message_id["id"])
#                                             await message.edit(embed=embed_alliance, view=dropdown_view)
#                                         else:
#                                             message = await channel.send(embed=embed_alliance, view=dropdown_view)
#                                             message_id["id"] = message.id
#                                             await utility_operations.saveJson(PATH + "coords_message.json", message_id)
#                             else:
#                                 # Split the members into two groups
#                                 mid_index = len(enemy_members) // 2
#                                 group1 = enemy_members[:mid_index]
#                                 group2 = enemy_members[mid_index:]
                                
#                                 groups = [group1, group2]
#                                 for group_index, group in enumerate(groups):
#                                     columns = 3  # Number of columns for the embed
#                                     embed_alliance = discord.Embed(title=f"Coordinates of {enemy_name}", color=discord.Color.from_rgb(255, 191, 0), timestamp=datetime.now(timezone.utc))
#                                     fields = [""] * columns

#                                     for idx, member in enumerate(group):
#                                         member_name = member['Name']
#                                         member_id = member['Id']
#                                         colonies = db_Alex.get_colonies(member_id)
#                                         found_colonies = db_Alex.found_colonies(member_id)

#                                         colony_info = f"**{member_name}**\n"
#                                         main_planet = db_Alex.get_player(member_id)
#                                         unix_time = utility_operations.get_unix_time(main_planet["MB_refresh_time"])
#                                         if main_planet['MB_status'] == "Up":
#                                             colony_info += f":white_check_mark: main SB{main_planet['MB_lvl']}\n"
#                                         else: 
#                                             colony_info += f":octagonal_sign: main SB{main_planet['MB_lvl']} - <t:{unix_time}:R>\n"

#                                         for colony in colonies:
#                                             coordinates = f"{colony['colo_coord']['x']},{colony['colo_coord']['y']}"
#                                             if coordinates != "-1,-1":
#                                                 colony_number = f"C{colony['number']}"
#                                                 SB_level = f"SB{colony['colo_lvl']}"

#                                                 unix_time = utility_operations.get_unix_time(colony["colo_refresh_time"])
                                                
#                                                 if colony['colo_status'] == "Up":
#                                                     colony_info += f":white_check_mark: {colony_number} - {SB_level} - {coordinates}\n"
#                                                 elif colony['colo_status'] == "Down":
#                                                     colony_info += f":octagonal_sign: {colony_number} - {SB_level} - {coordinates} - <t:{unix_time}:R>\n"
#                                                 else:
#                                                     colony_info += f":warning: {colony_number} - {SB_level} - {coordinates}\n"
                                        
#                                         for found_colony in found_colonies:
#                                             coordinates = f"{found_colony['X']},{found_colony['Y']}"
#                                             colony_info += f":grey_question: {coordinates}\n"

#                                         field_index = idx % columns
#                                         fields[field_index] += f"{colony_info}\n"
                                    
#                                     for i, field in enumerate(fields):
#                                         if field.strip():  # Only add non-empty fields
#                                             embed_alliance.add_field(name="", value=field, inline=True)
                                    
#                                     embed_alliance.set_footer(text="Last updated")
                                    
#                                     members = list(db_operations.get_all_members_GE2())
#                                     dropdown_view = dropdown.ScoreDropDownView(members)
#                                     guild = bot.get_guild(GUILD_ID)
#                                     if guild:
#                                         channel = guild.get_channel(CHANNEL_ID_COORDS)
#                                         if channel:
#                                             message_id_path = PATH + f"coords_message_group_{group_index + 1}.json"
#                                             message_id = await utility_operations.loadJson(message_id_path)
#                                             if message_id["id"] != 0:
#                                                 message = await channel.fetch_message(message_id["id"])
#                                                 if group_index == 0:
#                                                     await message.edit(embed=embed_alliance, view=None)
#                                                 else:
#                                                     await message.edit(embed=embed_alliance, view=dropdown_view)
#                                             else:
#                                                 message = ''
#                                                 if group_index == 0:
#                                                     message = await channel.send(embed=embed_alliance, view=None)
#                                                 else:
#                                                     message = await channel.send(embed=embed_alliance, view=dropdown_view)
#                                                 message_id["id"] = message.id
#                                                 await utility_operations.saveJson(message_id_path, message_id)
#             else:
#                 embed_alliance = discord.Embed(title=f"We are not at war", color=discord.Color.from_rgb(255, 191, 0))
#                 guild = bot.get_guild(GUILD_ID)
#                 if guild:
#                     channel = guild.get_channel(CHANNEL_ID_COORDS)
#                     if channel:
#                         message = await channel.fetch_message(message.id)
#                         if message:
#                             await message.edit(embed=embed_alliance)
#                         else:
#                             await channel.send(embed=embed_alliance)

#                         message_id = await utility_operations.loadJson(PATH + "coords_message.json")
#                         if message_id["id"] != 0:
#                             message = await channel.fetch_message(message_id["id"])
#                             await message.edit(embed=embed_alliance, view=None)
#                         else:
#                             message = await channel.send(embed=embed_alliance, view=None)
#                             message_id["id"] = message.id
#                             await utility_operations.saveJson(PATH + "coords_message.json", message_id)
#     except Exception as e:
#         if isinstance(e, discord.errors.NotFound):
#             print("Message was deleted, regenerating it...")
#         elif isinstance(e, discord.errors.HTTPException) and "Must be 1024 or fewer in length" in str(e):
#             print(f"Character limit reached or 1024")
#             split_needed = True
#         else:
#             print(f"An unexpected error occurred: {e}")

     

@tasks.loop(minutes=3)
async def info():
    global split_needed
    global number_of_splits
    print(split_needed, number_of_splits)
    current_time =''
    remaining_time = ''
    try:
        GE3_data = db_operations.find_opponent_GE3()
        if GE3_data:
            enemy = GE3_data["OpponentAllianceId"]
            if enemy != "":
                async with aiohttp.ClientSession() as session:
                    async with session.get(API_URL + utility_operations.replace_spaces(enemy)) as response:
                        if response.status == 200:
                            enemy_data = await response.json(content_type="text/plain")
                            enemy_name = enemy_data.get("Name", "Unknown")
                            enemy_members = enemy_data.get("Members", [])
                            
                            if not split_needed:
                                columns = 3  # Number of columns for the embed
                                embed_alliance = discord.Embed(title=f"Coordinates of {enemy_name}", color=discord.Color.from_rgb(255, 191, 0),timestamp=datetime.now(timezone.utc))
                                fields = [""] * columns

                                for idx, member in enumerate(enemy_members):
                                    member_name = member['Name']
                                    member_id = member['Id']
                                    colonies = db_Alex.get_colonies(member_id)
                                    found_colonies = db_Alex.found_colonies(member_id)

                                    colony_info = f"**{member_name}**\n"
                                    main_planet = db_Alex.get_player(member_id)
                                    current_time = datetime.now()
                                    time_difference = main_planet["MB_refresh_time"] - current_time - timedelta(hours=2)
                                    hours, remainder = divmod(time_difference.total_seconds(), 3600)
                                    minutes, _ = divmod(remainder, 60)
                                    remaining_time = f"{int(hours)}h{int(minutes)}m"

                                    if main_planet['MB_status'] == "Up":
                                        colony_info += f":white_check_mark: main SB{main_planet['MB_lvl']}\n"
                                    else: 
                                        colony_info += f":octagonal_sign: main SB{main_planet['MB_lvl']} - {remaining_time}\n"

                                    for colony in colonies:
                                        coordinates = f"{colony['colo_coord']['x']},{colony['colo_coord']['y']}"
                                        if coordinates != "-1,-1":
                                             colony_number = f"C{colony['number']}"
                                             SB_level = f"SB{colony['colo_lvl']}"

                                             current_time = datetime.now()
                                             time_difference = colony["colo_refresh_time"] - current_time - timedelta(hours=2)
                                             hours, remainder = divmod(time_difference.total_seconds(), 3600)
                                             minutes, _ = divmod(remainder, 60)
                                             remaining_time = f"{int(hours)}h{int(minutes)}m"

                                             if colony['colo_status'] == "Up":
                                                 colony_info += f":white_check_mark: {colony_number} - {SB_level} - {coordinates}\n"
                                             elif colony['colo_status'] == "Down":
                                                 colony_info += f":octagonal_sign: {colony_number} - {SB_level} - {coordinates} - {remaining_time}\n"
                                             else:
                                                 colony_info += f":warning: {colony_number} - {SB_level} - {coordinates}\n"
                                    
                                    for found_colony in found_colonies:
                                        coordinates = f"{found_colony['X']},{found_colony['Y']}"
                                        colony_info += f":grey_question: {coordinates}\n"

                                    field_index = idx % columns
                                    fields[field_index] += f"{colony_info}\n"
                                
                                for i, field in enumerate(fields):
                                    if field.strip():  # Only add non-empty fields
                                        embed_alliance.add_field(name="", value=field, inline=True)
                                
                                embed_alliance.set_footer(text="Last updated")
                                
                                members = list(db_operations.get_all_members_GE2())
                                dropdown_view = dropdown.ScoreDropDownView(members)
                                guild = bot.get_guild(GUILD_ID)
                                if guild:
                                    channel = guild.get_channel(CHANNEL_ID_COORDS)
                                    if channel:
                                        message_id = await utility_operations.loadJson(PATH + "coords_message.json")
                                        if message_id["id"] != 0:
                                            message = await channel.fetch_message(message_id["id"])
                                            await message.edit(embed=embed_alliance, view=dropdown_view)
                                            print('single message edited')
                                        else:
                                            message = await channel.send(embed=embed_alliance, view=dropdown_view)
                                            print('single message sent')
                                            message_id["id"] = message.id
                                            await utility_operations.saveJson(PATH + "coords_message.json", message_id)
                            else:
                                # Split the members into two groups
                                mid_index = len(enemy_members) // number_of_splits
                                groups = []
                                start_index = 0
                                
                                for i in range(1, number_of_splits + 1):
                                    if i == number_of_splits:  # Ensure the last group gets any remaining members
                                        groups.append(enemy_members[start_index:])
                                    else:
                                        end_index = start_index + mid_index
                                        groups.append(enemy_members[start_index:end_index])
                                        start_index = end_index
                                
                                
                                for group_index, group in enumerate(groups):
                                    columns = 3  # Number of columns for the embed
                                    embed_alliance = discord.Embed(title=f"Coordinates of {enemy_name}", color=discord.Color.from_rgb(255, 191, 0), timestamp=datetime.now(timezone.utc))
                                    fields = [""] * columns

                                    for idx, member in enumerate(group):
                                        member_name = member['Name']
                                        member_id = member['Id']
                                        colonies = db_Alex.get_colonies(member_id)
                                        found_colonies = db_Alex.found_colonies(member_id)

                                        colony_info = f"**{member_name}**\n"
                                        main_planet = db_Alex.get_player(member_id)
                                        current_time = datetime.now()
                                        time_difference = main_planet["MB_refresh_time"] - current_time - timedelta(hours=2)
                                        hours, remainder = divmod(time_difference.total_seconds(), 3600)
                                        minutes, _ = divmod(remainder, 60)
                                        remaining_time = f"{int(hours)}h{int(minutes)}m"

                                        if main_planet['MB_status'] == "Up":
                                            colony_info += f":white_check_mark: main SB{main_planet['MB_lvl']}\n"
                                        else: 
                                            colony_info += f":octagonal_sign: main SB{main_planet['MB_lvl']} - {remaining_time}\n"

                                        for colony in colonies:
                                            coordinates = f"{colony['colo_coord']['x']},{colony['colo_coord']['y']}"
                                            if coordinates != "-1,-1":
                                                colony_number = f"C{colony['number']}"
                                                SB_level = f"SB{colony['colo_lvl']}"

                                                current_time = datetime.now()
                                                time_difference = colony["colo_refresh_time"] - current_time - timedelta(hours=2)
                                                hours, remainder = divmod(time_difference.total_seconds(), 3600)
                                                minutes, _ = divmod(remainder, 60)
                                                remaining_time = f"{int(hours)}h{int(minutes)}m"
                                                
                                                if colony['colo_status'] == "Up":
                                                    colony_info += f":white_check_mark: {colony_number} - {SB_level} - {coordinates}\n"
                                                elif colony['colo_status'] == "Down":
                                                    colony_info += f":octagonal_sign: {colony_number} - {SB_level} - {coordinates} - {remaining_time}\n"
                                                else:
                                                    colony_info += f":warning: {colony_number} - {SB_level} - {coordinates}\n"
                                        
                                        for found_colony in found_colonies:
                                            coordinates = f"{found_colony['X']},{found_colony['Y']}"
                                            colony_info += f":grey_question: {coordinates}\n"

                                        field_index = idx % columns
                                        fields[field_index] += f"{colony_info}\n"
                                    
                                    for i, field in enumerate(fields):
                                        if field.strip():  # Only add non-empty fields
                                            embed_alliance.add_field(name="", value=field, inline=True)
                                    
                                    embed_alliance.set_footer(text="Last updated")
                                    
                                    members = list(db_operations.get_all_members_GE2())
                                    dropdown_view = dropdown.ScoreDropDownView(members)
                                    # creating embed
                                    guild = bot.get_guild(GUILD_ID)
                                    if guild:
                                        channel = guild.get_channel(CHANNEL_ID_COORDS)
                                        if channel:
                                            message_id_path = PATH + f"coords_message_group_{group_index + 1}.json"
                                            message_id = await utility_operations.loadJson(message_id_path)
                                            if message_id["id"] != 0:
                                                message = await channel.fetch_message(message_id["id"])
                                                if group_index == len(groups) - 1:
                                                    await message.edit(embed=embed_alliance, view=dropdown_view)
                                                    print(f'edited group {group_index} with drop')
                                                else:
                                                    await message.edit(embed=embed_alliance, view=None)
                                                    print(f'edited group {group_index}')
                                            else:
                                                message = ''
                                                if group_index == len(groups) - 1:
                                                    message = await channel.send(embed=embed_alliance, view=dropdown_view)
                                                    print(f'sent group {group_index} with drop')
                                                else:
                                                    message = await channel.send(embed=embed_alliance, view=None)
                                                    print(f'sent group {group_index}')
                                                message_id["id"] = message.id
                                                await utility_operations.saveJson(message_id_path, message_id)
                                
                                # deleting no war embed
                                message_id = await utility_operations.loadJson(PATH + "coords_message.json")
                                guild = bot.get_guild(GUILD_ID)
                                if guild:
                                    channel = guild.get_channel(CHANNEL_ID_COORDS)
                                    if channel:
                                        if message_id["id"] != 0:
                                            try:
                                                message_in_channel = await channel.fetch_message(message_id["id"])
                                                if message_in_channel:
                                                    await message_in_channel.delete()
                                                    print('deleted no war in groups')
                                                message_id["id"] = 0
                                            except Exception as e:
                                                message_id["id"] = 0
                                                print('no war is 0 from groups')
                                await utility_operations.saveJson(PATH + "coords_message.json", message_id)

            else:
                # creating embed
                number_of_splits = 1
                split_needed = False
                embed_alliance = discord.Embed(title=f"We are not at war", color=discord.Color.from_rgb(255, 191, 0))
                guild = bot.get_guild(GUILD_ID)
                if guild:
                    channel = guild.get_channel(CHANNEL_ID_COORDS)
                    if channel:
                        message_id = await utility_operations.loadJson(PATH + "coords_message.json")
                        if message_id["id"] != 0:
                            message = await channel.fetch_message(message_id["id"])
                            await message.edit(embed=embed_alliance, view=None)
                            print('no war edited')
                        else:
                            async for msg in channel.history(limit=20):
                                try:
                                    await msg.delete()
                                    print("cleared channel")
                                except Exception as e:
                                    print(f"couldn't delete: {e}")
                            message = await channel.send(embed=embed_alliance, view=None)
                            print('no war send')
                            message_id["id"] = message.id
                            await utility_operations.saveJson(PATH + "coords_message.json", message_id)
                        
                        # deleting other embeds (groups)
                        for i in range(1,7):
                                message = await utility_operations.loadJson(f"{PATH}coords_message_group_{i}.json")
                                guild = bot.get_guild(GUILD_ID)
                                if guild:
                                    channel = guild.get_channel(CHANNEL_ID_COORDS)
                                    if channel:
                                        message_id = message["id"]
                                        if message_id:
                                            try:
                                                message_in_channel = await channel.fetch_message(message_id)
                                                if message_in_channel:
                                                    await message_in_channel.delete()
                                                    print(f'deleted group {i} from no war')
                                                message["id"] = 0
                                            except Exception as e:
                                                message["id"] = 0
                                                print(f'exception group {i} from no war but is 0')
                                await utility_operations.saveJson(f"{PATH}coords_message_group_{i}.json", message)

    except Exception as e:
        if isinstance(e, discord.errors.NotFound):
            print("Message was deleted, regenerating it...")
            message_id = await utility_operations.loadJson(PATH + "coords_message.json")
            message_id['id'] = 0
            await utility_operations.saveJson(PATH + "coords_message.json", message_id)
            for i in range(1,17):
                message = await utility_operations.loadJson(f"{PATH}coords_message_group_{i}.json")
                message["id"] = 0
                message = await utility_operations.saveJson(f"{PATH}coords_message_group_{i}.json", message)


        elif isinstance(e, discord.errors.HTTPException) and "Must be 1024 or fewer in length" in str(e):
            print(f"Character limit reached of 1024")
            split_needed = True
            number_of_splits += 1
            
        elif isinstance(e, discord.errors.HTTPException) and "Embed size exceeds maximum size of 6000" in str(e):
            print(f"embed size of 6000 reached")
            split_needed = True
            number_of_splits += 1
        else:
            print(f"An unexpected error occurred in info: {e}")

bot.run(os.getenv('token_development'))