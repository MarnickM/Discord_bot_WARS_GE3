import discord
from database import database
import asyncio
import aiohttp
import discord
from datetime import datetime, timedelta

db_operations = database.DatabaseConnection()


class ScoreDropDown(discord.ui.Select):
    def __init__(self, members, index):
        members = sorted(members, key=lambda x: x['points_gained'], reverse=True)
        options = [
            discord.SelectOption(label=f"{member['points_gained']} - {member['Name']}", value=member['Name'], emoji="⭐")
            for member in members
        ]
        member_count = len(members)
        if member_count <= 25:
            super().__init__(placeholder=f"View scores of the members", options=options)
        else:
            super().__init__(placeholder=f"View scores of the members (Part{index})", options=options)

    # to send a message to the user when they select an option
    # async def callback(self, interaction: discord.Interaction):
    #     selected_member = self.values[0]
    #     player_data = db_operations.find_player(selected_member)
    #     if player_data:
    #         score = player_data['total_warpoints']
    #         await interaction.response.send_message(f"{selected_member}'s score: {score} <:Warpoints:1206215489349619722>", ephemeral=True)
    #     else:
    #         await interaction.response.send_message(f"No data found for {selected_member}", ephemeral=True)

class ScoreDropDownView(discord.ui.View):
    def __init__(self, members):
        super().__init__()
        chunk_size = 25
        for i in range(0, len(members), chunk_size):
            chunk = members[i:i + chunk_size]
            dropdown = ScoreDropDown(chunk, index=(i // chunk_size) + 1)
            self.add_item(dropdown)


class ColonyDropDown(discord.ui.Select):
    def __init__(self, player_data, colonies):
        self.player_data = player_data
        self.colonies = colonies
        options = []
        
        # Initialize the dropdown options
        self.update_options()
        super().__init__(placeholder=f"View colonies of {player_data['Name']}", options=options)

    def update_options(self):
        """Updates the dropdown options with the current state of colonies."""
        self.options = []  # Clear current options
        current_time = datetime.now()  # Use local time

        # Add the main planet first (always exists)
        self.options.append(discord.SelectOption(
            label=f"{self.player_data['Name']}",
            value="Main Planet",
            emoji="🌍"
        ))

        # Iterate over colonies (C0 to C11)
        for i in range(len(self.colonies)):
            colony_name = f"Colony {i+1}"
            colony_data = self.colonies[i]
            
            if colony_data:
                # Parse destruction time (colony[0] is the destruction timestamp)
                destruction_time_str = colony_data[0]
                destruction_time = datetime.strptime(destruction_time_str, "%Y-%m-%d %H:%M:%S")
                respawn_time = destruction_time + timedelta(hours=3)  # Default 3-hour respawn time

                # Determine if colony is still destroyed or has respawned
                if current_time < respawn_time:
                    # Colony still destroyed, show time until respawn
                    time_left = respawn_time - current_time
                    time_left_str = f"Up in {time_left.seconds // 3600}h {time_left.seconds % 3600 // 60}m"
                    label = f"{colony_name} - Destroyed {colony_data[1]} - {time_left_str}"

                    # Add explosion emoji to represent destruction
                    self.options.append(discord.SelectOption(label=label, value=colony_name, emoji="💥", description="placeholder"))
                else:
                    # Colony has respawned, display SB level
                    label = f"{colony_name} - SB {colony_data[2]} - Coordinates ({colony_data[1]})"
                    self.options.append(discord.SelectOption(label=label, value=colony_name, emoji="🪐", description="placeholder"))
            else:
                # No data available for this colony, display Not Found
                self.options.append(discord.SelectOption(label=f"{colony_name} - Not Found", value=colony_name, emoji="❔", description="placeholder"))

    async def callback(self, interaction: discord.Interaction):
        selected_colony = self.values[0]
        name = interaction.user.name
        await interaction.response.send_message(f"Selected: {selected_colony} by {name}", ephemeral=True)

class ColonyDropDownView(discord.ui.View):
    def __init__(self, enemy_player_info_dashboard):
        super().__init__()
        self.dropdown_items = []
        
        # Fetch player colony data from the database
        colony_data = db_operations.find_player(enemy_player_info_dashboard['Name'])
        nr_of_colonies = len(enemy_player_info_dashboard['planets'])
        colonies = [colony_data.get(f"C{i}", []) for i in range(nr_of_colonies)]
            
        dropdown = ColonyDropDown(enemy_player_info_dashboard, colonies)
        self.dropdown_items.append(dropdown)
        self.add_item(dropdown)

    async def update_all_dropdowns(self):
        """Updates all dropdowns in the view with the latest data."""
        for dropdown in self.dropdown_items:
            dropdown.update_options()  # Update the options in each dropdown dynamically
        # This will automatically reflect in the view without needing to clear or re-add them

async def update_dropdowns_periodically(view):
    """
    Periodically update dropdowns every 60 seconds to reflect time-based changes.
    """
    while True:
        # Update all dropdowns within the view
        await view.update_all_dropdowns()

        # Wait for the next update (60 seconds)
        await asyncio.sleep(60)






# class ColonyDropDown(discord.ui.Select):
#     def __init__(self, player_data, colonies):
#         options = []
        
#         # Add the main planet first (always exists)
#         options.append(discord.SelectOption(label=f"Main Planet - {player_data['Name']}", value="Main Planet"))
        
#         # Add colonies with coordinates or "Not found" if empty
#         for i in range(len(colonies)):
#             colony_name = f"Colony {i+1}"
#             coordinates = colonies[i]
            
#             if coordinates:
#                 coord_str = f"({coordinates[1]}) - {coordinates[2]}"  # Using X, Y coords
#                 options.append(discord.SelectOption(label=f"{colony_name} - {coord_str}", value=colony_name))
#             else:
#                 options.append(discord.SelectOption(label=f"{colony_name} - Not Found", value=colony_name))
        
#         super().__init__(placeholder=f"View colonies of {player_data['Name']}", options=options)

#     async def callback(self, interaction: discord.Interaction):
#         selected_colony = self.values[0]
#         await interaction.response.send_message(f"Selected: {selected_colony}", ephemeral=True)

# class ColonyDropDownView(discord.ui.View):
#     def __init__(self, enemy_alliance_players):
#         super().__init__()
#         # For each enemy player, create a dropdown menu
#         for player in enemy_alliance_players:
#             # Fetch player colony data from the database
#             colony_data = db_operations.find_player(player['Name'])
            
#             # Extract colonies (C0 to C11)
#             colonies = [colony_data.get(f"C{i}", []) for i in range(12)]
            
#             dropdown = ColonyDropDown(player, colonies)
#             self.add_item(dropdown)


