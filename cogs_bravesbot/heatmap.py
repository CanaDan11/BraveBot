import asyncio
import discord
import json
import os
import numpy as np
import random as rdm
import requests
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import matplotlib.cm as cm
from discord.ext import commands
from discord.ext.commands import guild_only

API_BASE_URL = "https://www.rslashfakebaseball.com/api/plateappearances/pitching"
API_BASE_URL_B = "https://www.rslashfakebaseball.com/api/plateappearances/batting"

class General(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.image_counter = 0  # Counter for naming the image files
        self.image_folder = "plots"  # Folder name for saving the plots
        os.makedirs(self.image_folder, exist_ok=True)  # Create the folder if it doesn't exist

    @commands.command(brief="!ping Returns pong if bot is up")
    @guild_only()
    async def ping(self, ctx):
        """
        Returns pong if bot is up.

        Usage: !ping
        """
        await ctx.send("pong")
        
    @commands.command(brief="!last <League> <player id> <number of pitches> Fetches data and plots a graph.")
    @guild_only()
    async def last(self, ctx, league: str, player_id: str, num_pitches: int):
        """
        Fetches data from the specified league and player id and plots a graph.

        Usage: !last <League> <player id> <number of pitches>
        """
        print(1)	
        # Fetch player's name
        player_info_url = f"https://www.rslashfakebaseball.com/api/players/id/{player_id}"
        player_info = requests.get(player_info_url).json()
        player_name = player_info['playerName'] if 'playerName' in player_info else f"Player {player_id}"
        data = (requests.get(f"{API_BASE_URL}/{league}/{player_id}")).json()
        print(player_name)

        # Fetch data
        data = requests.get(f"{API_BASE_URL}/{league}/{player_id}").json()
        seasons_sessions = [f"{p['season']}.{p['session']}.{p['inning']}.{p['playNumber']}" for p in data]
        seasons_sessions_d = [f"{p['season']}.{p['session']}.{p['inning']}" for p in data]
        pitches = [p['pitch'] for p in data]
      
        print(seasons_sessions_d) 
    
        if pitches:
            # Limit the number of pitches based on user input
            num_pitches = min(num_pitches, len(pitches))  # Ensure num_pitches does not exceed the total number of pitches
            seasons_sessions = seasons_sessions[-num_pitches:]  # Take the last num_pitches elements
            pitches = pitches[-num_pitches:]  # Take the last num_pitches elements
            
            fig_height = 6.0
            # Determine figure size based on number of ticks
            fig_width = num_pitches * 0.6  # Adjust this factor as needed
            #fig_height = fig_width * 0.7  # Maintain aspect ratio, adjust as needed
            # Automatically adjust axis limits
            #plt.autoscale(enable=True, axis='both', tight=None)
            plt.figure(figsize=(fig_width, fig_height), tight_layout=True)
              
            print(5)
            plt.xticks(rotation=45, ha='right') # Rotate x-axis labels for better visibility
            plt.yticks(np.arange(0, 1001, 100), labels=[str(i) if i % 200 == 0 else '' for i in range(0, 1001, 100)])  # Set y-axis ticks with spaces between each 100
            plt.ylim(0, 1000)
            plt.xlabel('Season.Session.Inning')
            plt.ylabel('Pitch')
            plt.title(f'Last {num_pitches} pitches thrown by {player_name} in {league}')
            plt.grid(True, which='both', axis='y', color='gray', linestyle='--', linewidth=0.5, alpha=0.9)

            # Plot the graph
            plt.scatter(seasons_sessions, pitches, marker='o', color='red')  # Make the dots red
        
            for i, (x, y) in enumerate(zip(seasons_sessions, pitches)):
                plt.annotate(f'{y}', (x, y), textcoords="offset points", xytext=(0,10), ha='right', color='red')
        
            for i in range(len(seasons_sessions) - 1):
                plt.plot([seasons_sessions[i], seasons_sessions[i+1]], [pitches[i], pitches[i+1]], color='grey', linestyle='dashed', alpha=0.5)

            
            # Save the plot to the specified folder
            filename = f'{self.image_folder}/plot_{self.image_counter}.png'
            print(6)
            plt.savefig(filename, format='png')
            print(7)

            # Read the saved image file
            with open(filename, 'rb') as file:
                print(8)
                plot_data = discord.File(file)
                print(9)

            # Send the plot as a message
            await ctx.send(file=plot_data)

            # Increment the image counter
            self.image_counter += 1	

        else:
            await ctx.send("No data available for the player in the specified league.")
            
    @commands.command(brief="!hm <League> <player id> Fetches data and plots a heatmap.")
    @guild_only()
    async def hm(self, ctx, league: str, player_id: str):
        """
        Fetches data from the specified league and player id and plots a heatmap.

        Usage: !hm <League> <player id>
        """
        # Fetch player's name
        player_info_url = f"https://www.rslashfakebaseball.com/api/players/id/{player_id}"
        player_info = requests.get(player_info_url).json()
        player_name = player_info['playerName'] if 'playerName' in player_info else f"Player {player_id}"
    
        # Fetch data
        data = requests.get(f"{API_BASE_URL}/{league}/{player_id}").json()
        seasons_sessions = [f"{p['season']}.{p['session']}.{p['inning']}.{p['playNumber']}" for p in data]
        pitches = [p['pitch'] for p in data]
  
        if pitches:
            # Normalize the data to calculate percentages
           ## num_pitches = len(pitches)
           ## percentages = [(pitch / num_pitches) * 100 for pitch in pitches]  
            
            # Create a heatmap
            plt.figure(figsize=(10, 6))

            # Set bins for x-axis
            x_bins = np.arange(0, min(len(seasons_sessions), 101), 25)

            plt.hist2d(range(len(seasons_sessions)), pitches, bins=[x_bins, np.arange(0, 1001, 100)], cmap='hot_r')
            plt.colorbar(label='Frequency of Pitches')
            plt.xticks(x_bins, rotation=45, ha='right')  # Set x-axis ticks every 25
            plt.yticks(np.arange(0, 1001, 100))  # Set y-axis ticks every 100
            plt.xlabel('')
            plt.ylabel('')
            plt.title(f'Heatmap of Pitches thrown by {player_name} in League {league}')
            plt.tight_layout()

            # Add grid lines
            plt.grid(True)

            # Save the heatmap to the specified folder
            filename = f'{self.image_folder}/heatmap_{self.image_counter}.png'
            plt.savefig(filename, format='png')

             # Read the saved image file
            with open(filename, 'rb') as file:
           
                 heatmap_data = discord.File(file)

            # Send the heatmap as a message
            await ctx.send(file=heatmap_data)

            # Increment the image counter
            self.image_counter += 1
            
        else:
            await ctx.send("No data available for the player in the specified league.")

    @commands.command(brief="!react <League> <player id> <lower range number> <high range number> Fetches data and plots a graph.")
    @guild_only()
    async def react(self, ctx, league: str, player_id: str, lower_range: int, high_range: int):
        """
        Fetches data from the specified league and player id and plots a graph.

        Usage: !react <League> <player id> <lower range number> <high range number>
        """
        # Fetch player's name
        player_info_url = f"https://www.rslashfakebaseball.com/api/players/id/{player_id}"
        player_info = requests.get(player_info_url).json()
        player_name = player_info.get('playerName', f"Player {player_id}")
        print(test1)
        # Fetch data
        data = requests.get(f"{API_BASE_URL}/{league}/{player_id}").json()
        if not data:
            await ctx.send("No data available for the player in the specified league.")
            return
        print(test2)
        # Filter data based on pitch number range
        filtered_data = [p for p in data if lower_pitch <= p['pitch'] <= higher_pitch]
        seasons_sessions = [f"{p['season']}.{p['session']}.{p['inning']}.{p['playNumber']}" for p in filtered_data]
        pitches = [p['pitch'] for p in filtered_data]
        print(test3)
        if pitches:
            # Determine the number of pitches to display
            num_pitches = len(pitches)

            # Create the plot
            fig_height = 6.0
            fig_width = num_pitches * 0.6
            plt.figure(figsize=(fig_width, fig_height), tight_layout=True)
            plt.xticks(rotation=45, ha='right')
            plt.yticks(np.arange(0, 1001, 100), labels=[str(i) if i % 200 == 0 else '' for i in range(0, 1001, 100)])
            plt.ylim(0, 1000)
            plt.xlabel('Game')
            plt.ylabel('Pitch')
            plt.title(f'Pitches thrown by {player_name} in {league} (Range: {lower_range}-{high_range})')
            plt.grid(True)

            # Plot the filtered pitches as blue dots
            seasons_sessions = [f"{p['season']}.{p['session']}.{p['inning']}.{p['playNumber']}" for p in data]
            plt.scatter(seasons_sessions, pitches, marker='o', color='blue')

            # Plot the line connecting the pitches as a solid blue line
            for i in range(len(seasons_sessions) - 1):
                plt.plot([seasons_sessions[i], seasons_sessions[i+1]], [pitches[i], pitches[i+1]], color='blue')
            
            # Save the plot
            filename = f'{self.image_folder}/plot_{self.image_counter}.png'
            plt.savefig(filename, format='png')

            # Send the plot as a message
            with open(filename, 'rb') as file:
                plot_data = discord.File(file)
            await ctx.send(file=plot_data)

            # Increment the image counter
            self.image_counter += 1
        else:
            await ctx.send(f"No pitches found in the specified range for the player in the specified league.")

    @commands.command(brief="!pitch <League> <player id> <number of pitches> Fetches data and plots a polar plot.")
    @commands.guild_only()
    async def pitch(self, ctx, league: str, player_id: str, num_pitches: int):
        """
        Fetches data from the specified league and player id and plots a polar plot.

        Usage: !pitch <League> <player id> <number of pitches>
        """
        # Fetch player's name
        player_info_url = f"https://www.rslashfakebaseball.com/api/players/id/{player_id}"
        player_info = requests.get(player_info_url).json()
        player_name = player_info['playerName'] if 'playerName' in player_info else f"Player {player_id}"

        # Fetch data
        data = requests.get(f"{API_BASE_URL}/{league}/{player_id}").json()
        pitches = [p['pitch'] for p in data]

        if pitches:
            # Limit the number of pitches based on user input
            num_pitches = min(num_pitches, len(pitches))  # Ensure num_pitches does not exceed the total number of pitches
            pitches = pitches[-num_pitches:]  # Take the last num_pitches elements

            # Create polar plot
            fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})
            theta = np.linspace(0, 2*np.pi, num_pitches, endpoint=False)  # Angles for polar plot
            r = np.arange(num_pitches) * 2 * np.pi / num_pitches  # Radii represent normalized distance
            ax.plot(theta, r, marker='o', color='red')  # Plot pitches

            # Set the title and labels
            ax.set_title(f'Last {num_pitches} pitches thrown by {player_name} in {league}')
            ax.set_rlabel_position(90)

            # Save the plot to the specified folder
            filename = f'{self.image_folder}/plot_{self.image_counter}.png'
            plt.savefig(filename, format='png')

            # Read the saved image file
            with open(filename, 'rb') as file:
                
                plot_data = discord.File(file, filename="plot.png")

            # Send the plot as a message
            await ctx.send(file=plot_data)

            # Increment the image counter
            self.image_counter += 1

        else:
            await ctx.send("No data available for the player in the specified league.")

    #########below this line is for batter info and commands#####################################

    @commands.command(brief="!swinglast <League> <player id> <number of swings> Fetches data and plots a graph.")
    @guild_only()
    async def swinglast(self, ctx, league: str, player_id: str, num_swings: int):
        """
        Fetches data from the specified league and player id and plots a graph.

        Usage: !swinglast <League> <player id> <number of swings>
        """
        print(15)    
        # Fetch player's name
        player_info_url = f"https://www.rslashfakebaseball.com/api/players/id/{player_id}"
        player_info = requests.get(player_info_url).json()
        player_name = player_info['playerName'] if 'playerName' in player_info else f"Player {player_id}"
        data = (requests.get(f"{API_BASE_URL_B}/{league}/{player_id}")).json()
        print(player_name)

        # Fetch data
        data = requests.get(f"{API_BASE_URL_B}/{league}/{player_id}").json()
        seasons_sessions = [f"{p['season']}.{p['session']}.{p['inning']}.{p['playNumber']}" for p in data]
        swings = [p['swing'] for p in data]
  
        print(swings) 
    
        if swings:
            # Limit the number of swings based on user input
            num_swings = min(num_swings, len(swings))  # Ensure num_swings does not exceed the total number of swings
            seasons_sessions = seasons_sessions[-num_swings:]  # Take the last num_swings elements
            swings = swings[-num_swings:]  # Take the last num_swings elements
        
            # Determine figure size based on number of ticks
            fig_width = num_swings * 0.6  # Adjust this factor as needed
            fig_height = fig_width * 0.7  # Maintain aspect ratio, adjust as needed
        
            plt.figure(figsize=(fig_width, fig_height))
        
            plt.xticks(rotation=45, ha='right')  # Rotate x-axis labels for better visibility
            plt.yticks(np.arange(0, 1001, 100), labels=[str(i) if i % 200 == 0 else '' for i in range(0, 1001, 100)])  # Set y-axis ticks with spaces between each 100
            plt.ylim(0, 1000)
            plt.xlabel('Game')
            plt.ylabel('Swing')
            plt.title(f'Last {num_swings} swings by {player_name} in {league}')
            plt.grid(True)
        
            print(16)
        
            # Plot the graph
            plt.scatter(seasons_sessions, swings, marker='o', color='red')  # Make the dots red
    
            for i, (x, y) in enumerate(zip(seasons_sessions, swings)):
                plt.annotate(f'{y}', (x, y), textcoords="offset points", xytext=(0,10), ha='right', color='red')
    
            for i in range(len(seasons_sessions) - 1):
                plt.plot([seasons_sessions[i], seasons_sessions[i+1]], [swings[i], swings[i+1]], color='grey', linestyle='dashed')

            # Save the plot to the specified folder
            filename = f'{self.image_folder}/plot_{self.image_counter}.png'
            print(17)
            plt.savefig(filename, format='png')
            print(18)

            # Read the saved image file
            with open(filename, 'rb') as file:
               print(19)
               plot_data = discord.File(file)
               print(20)

            # Send the plot as a message
            await ctx.send(file=plot_data)

            # Increment the image counter
            self.image_counter += 1    

        else:
            await ctx.send("No data available for the player in the specified league.")
async def setup(client):
    await client.add_cog(General(client))
