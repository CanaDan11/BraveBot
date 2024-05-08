import discord
import os
import numpy as np
import requests
import plotly.graph_objects as go
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

    @commands.command(brief="!last <League> <player id> <number of pitches> Fetches data and plots a graph.")
    @guild_only()
    async def last(self, ctx, league: str, player_id: str, num_pitches: int):
        """
        Fetches data from the specified league and player id and plots a graph.

        Usage: !last <League> <player id> <number of pitches>
        """
        # Fetch player's name
        player_info_url = f"https://www.rslashfakebaseball.com/api/players/id/{player_id}"
        player_info = requests.get(player_info_url).json()
        player_name = player_info['playerName'] if 'playerName' in player_info else f"Player {player_id}"
        data = requests.get(f"{API_BASE_URL}/{league}/{player_id}").json()
        print(1)
        # Fetch data
        seasons_sessions = [f"{p['season']}.{p['session']}.{p['inning']}.{p['playNumber']}" for p in data]
        pitches = [p['pitch'] for p in data]
        print(2)
        if pitches:
            # Limit the number of pitches based on user input
            num_pitches = min(num_pitches, len(pitches))  # Ensure num_pitches does not exceed the total number of pitches
            seasons_sessions = seasons_sessions[-num_pitches:]  # Take the last num_pitches elements
            pitches = pitches[-num_pitches:]  # Take the last num_pitches elements
            print(3)
            # Create plotly scatter plot
                fig = go.Figure(data=go.Scatter(x=seasons_sessions, y=pitches, mode='markers', marker=dict(color='red')))
                fig.update_layout(title=f'Last {num_pitches} pitches thrown by {player_name} in {league}',
                                  xaxis_title='Season.Session.Inning',
                                  yaxis_title='Pitch')
                await ctx.send(embed=fig.to_image(format="png"))
            print(4)
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
        print(1)
        # Fetch data
        data = requests.get(f"{API_BASE_URL}/{league}/{player_id}").json()
        seasons_sessions = [f"{p['season']}.{p['session']}.{p['inning']}.{p['playNumber']}" for p in data]
        pitches = [p['pitch'] for p in data]
        print(2)
        if pitches:
            # Create heatmap
            layout = go.Layout(
                autosize=False,
                width=1000,
                height=500,
            )
            fig = go.Figure(layout=layout)
            fig.add_trace(go.Histogram2d(
                colorscale=[[0, 'rgb(253,34,5)'], [0.25, 'rgb(253,192,5)'], [0.5, 'rgb(233,253,5)'],
                            [0.75, 'rgb(113,196,5)'], [1, 'rgb(5,196,19)']],
                reversescale=True,
                xbingroup=4,
                ybingroup=10,
                ygap=2,
                xgap=2,
                autobinx=False,
                xbins=dict(start=0, end=100, size=25),
                autobiny=False,
                ybins=dict(start=0, end=1000, size=100),
                x=seasons_sessions,
                y=pitches
            ))
            fig.update_xaxes(dtick=25)
            fig.update_yaxes(dtick=100)
            fig.update_traces(colorbar=dict(title="Num pitches"))
            fig.update_layout(title=f'Heatmap of Pitches thrown by {player_name} in League {league}',
                              xaxis_title='Game',
                              yaxis_title='Frequency of Pitches',
                              annotations=[],  # Remove annotations
                              margin_l=200,
                              margin_r=200)
            await ctx.send(embed=fig.to_image(format="png"))
            print(3)
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

        # Fetch data
        data = requests.get(f"{API_BASE_URL}/{league}/{player_id}").json()
        if not data:
            await ctx.send("No data available for the player in the specified league.")

        # Filter data based on pitch number range
        filtered_data = [p for p in data if lower_range <= p['pitch'] <= high_range]
        seasons_sessions = [f"{p['season']}.{p['session']}.{p['inning']}.{p['playNumber']}" for p in filtered_data]
        pitches = [p['pitch'] for p in filtered_data]

        if pitches:
            # Create plotly scatter plot
            fig = go.Figure(data=go.Scatter(x=seasons_sessions, y=pitches, mode='markers', marker=dict(color='blue')))
            fig.update_layout(title=f'Pitches thrown by {player_name} in {league} (Range: {lower_range}-{high_range})',
                              xaxis_title='Game',
                              yaxis_title='Pitch')
            await ctx.send(embed=fig.to_image(format="png"))

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
            fig = go.Figure(data=go.Scatterpolar(theta=np.linspace(0, 2 * np.pi, num_pitches),
                                                  r=np.arange(num_pitches) * 2 * np.pi / num_pitches,
                                                  mode='markers',
                                                  marker=dict(color='red')))
            fig.update_layout(title=f'Last {num_pitches} pitches thrown by {player_name} in {league}')
            await ctx.send(embed=fig.to_image(format="png"))

        else:
            await ctx.send("No data available for the player in the specified league.")

    @commands.command(brief="!swinglast <League> <player id> <number of swings> Fetches data and plots a graph.")
    @guild_only()
    async def swinglast(self, ctx, league: str, player_id: str, num_swings: int):
        """
        Fetches data from the specified league and player id and plots a graph.

        Usage: !swinglast <League> <player id> <number of swings>
        """
        # Fetch player's name
        player_info_url = f"https://www.rslashfakebaseball.com/api/players/id/{player_id}"
        player_info = requests.get(player_info_url).json()
        player_name = player_info['playerName'] if 'playerName' in player_info else f"Player {player_id}"
        data = (requests.get(f"{API_BASE_URL_B}/{league}/{player_id}")).json()

        # Fetch data
        data = requests.get(f"{API_BASE_URL_B}/{league}/{player_id}").json()
        seasons_sessions = [f"{p['season']}.{p['session']}.{p['inning']}.{p['playNumber']}" for p in data]
        swings = [p['swing'] for p in data]

        if swings:
            # Limit the number of swings based on user input
            num_swings = min(num_swings, len(swings))  # Ensure num_swings does not exceed the total number of swings
            seasons_sessions = seasons_sessions[-num_swings:]  # Take the last num_swings elements
            swings = swings[-num_swings:]  # Take the last num_swings elements

            # Create plotly scatter plot
            fig = go.Figure(data=go.Scatter(x=seasons_sessions, y=swings, mode='markers', marker=dict(color='red')))
            fig.update_layout(title=f'Last {num_swings} swings by {player_name} in {league}',
                              xaxis_title='Game',
                              yaxis_title='Swing')
            await ctx.send(embed=fig.to_image(format="png"))

        else:
            await ctx.send("No data available for the player in the specified league.")

async def setup(client):
    await client.add_cog(General(client))