@commands.command(brief="!react <League> <player id> <lower range number> <high range number> Fetches data and plots a graph.")
    @guild_only()
    async def react(self, ctx, league: str, player_id: str, lower_range: int, high_range: int):
        """
        Fetches data from the specified league and player id and plots a graph.

        Usage: !react <League> <player id> <lower range number> <high range number>
        """
        # Fetch player's name
        player_info_url = f"https://www.rslashfakebaseball.com/api/players/id/{player_id}"
        player_info = requests.get(player_info_url)
        player_data = player_info.json()
        player_name = player_data.get('playerName', f"Player {player_id}")

        data = requests.get(f"{API_BASE_URL}/{league}/{player_id}").json()

        if not data:
            await ctx.send("No data available for the player in the specified league.")
            return
    
        # Filter data based on pitch number range
        filtered_data = []
        for item in data:
            if lower_range <= item['pitch'] <= high_range:
                filtered_data.append(item)
            
        # Extract pitches from filtered data
        pitches = [p['pitch'] for p in filtered_data]

        # Filter data for immediate pitches before and after each pitch in the specified range
        before_pitches = []
        after_pitches = []
        for pitch in pitches:
            before_pitches.append(pitch - 1)  # Immediate pitch before
            after_pitches.append(pitch + 1)   # Immediate pitch after

        seasons_sessions = [f"{p['season']}.{p['session']}" for p in filtered_data]
        innings = [f"{p['inning']}" for p in filtered_data]

        if pitches:
            # Combine all pitches for plotting
            all_pitches = sorted(set(before_pitches + after_pitches + pitches))

            # Create the plot
            fig_height = 6.0
            fig_width = len(all_pitches) * 0.6
            plt.figure(figsize=(fig_width, fig_height), tight_layout=True)

            # Plot the filtered pitches within range as blue dots and connect them with solid line
            plt.plot([all_pitches.index(pitch) for pitch in pitches], pitches, marker='o', color='blue', linestyle='-')

            # Plot the immediate pitch prior using a red dotted line
            for pitch in before_pitches:
                if pitch in all_pitches:
                    plt.plot(all_pitches.index(pitch), pitch, marker='o', color='red')

            # Plot the immediate pitch after using a black dotted line
            for pitch in after_pitches:
                if pitch in all_pitches:
                    plt.plot(all_pitches.index(pitch), pitch, marker='o', color='black')

            # Connect the points with broken lines in their respective colors
            for i in range(len(pitches)):
                if before_pitches[i] in all_pitches:
                    plt.plot([all_pitches.index(before_pitches[i]), all_pitches.index(pitches[i])], [before_pitches[i], pitches[i]], color='red', linestyle='--')
                if after_pitches[i] in all_pitches:
                    plt.plot([all_pitches.index(pitches[i]), all_pitches.index(after_pitches[i])], [pitches[i], after_pitches[i]], color='black', linestyle='--')

            # Combine seasons_sessions and innings labels
            x_labels = [f"{season}\n{inning}" for season, inning in zip(seasons_sessions, innings)]

            # Set the x-axis labels and their positions
            plt.xticks(range(len(x_labels)), x_labels)

            plt.yticks(np.arange(0, 1001, 100), labels=[str(i) if i % 200 == 0 else '' for i in range(0, 1001, 100)])
            plt.ylim(0, 1000)
            plt.xlabel('Game')
            plt.ylabel('Pitch')
            plt.title(f'Pitches thrown by {player_name} in {league} (Range: {lower_range}-{high_range})')
            plt.grid(True, which='both', axis='y', color='gray', linestyle='--', linewidth=0.5, alpha=0.9)

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
