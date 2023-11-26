# Python for Football Manager 2023 Scouting

## Overview
Football Manager 2023 offers a vast and intricate database of player attributes, performance statistics, and potential within the simulated footballing world. However, harnessing this wealth of data for comprehensive scouting and analysis can be a complex task. This project, "Python for Football Manager 2023 Scouting," presents a solution by leveraging Python scripts to streamline the extraction and compilation of player data from FM 23.

By utilizing these scripts, users can gather player information, tracking changes in attributes and performance over time. The project facilitates the creation of a centralized and dynamic database that empowers Football Manager enthusiasts to delve deeper into player development trends, identify rising stars, and make strategic decisions within the game.

Whether you're an avid FM player aiming to gain a competitive edge through thorough scouting or a data enthusiast seeking to explore trends and patterns within the game's simulated world, this project offers a robust framework to facilitate data-driven insights and informed decision-making.

## Features
- **Data Extraction:** Extract player attributes and statistics from Football Manager 2023.
- **Compilation:** Compile seasons data into a structured database for easy analysis.
- **Historical Tracking:** Track player progression and changes in attributes over time.
- **Customization:** Adapt scripts for specific scouting needs or preferences.

## Goals
- **Streamlined Scouting:** Simplify the process of collecting and organizing player data from FM 23.
- **Data-driven Insights:** Enable users to derive meaningful insights by analyzing historical player information.
- **User Flexibility:** Provide customization options for tailored scouting experiences.

## Processing exports
The first step on the ladder is the file *Exports processor*. For this method to work properly, you should run this script twice a year so you always have the most recent data. This allows you to make mid-season signings and also to avoid losing data. In FM23, when a player moves between clubs his season stats are wiped and you can no longer export it through the Player Search screen. This is a common occurence because many players change clubs during the mid-season January window if you are in Europe. Also always remember to INCLUDE players from your club on the search.

To run this, you need to create 4 files of data:
- **FM Stats** -> Using the *Python - Stats.fmf* view, export a list of as many players as you want on FM23. Just go into the Player Search, hit CTRL+A and CTRL+P to print it as a Web Page to an HTML file. Always check the shape of the dataframe that comes from this html file. Exporting a large amount of players on FM is always a bit buggy.
- **FM Attributes** -> A similar approach from before but using the *Python - Attributes.fmf* file. While the above exports the Stats (like Goals, Assists, Passes) this one exports the Attributes. If you are playing with masked attributes on, the script will consider the worst case scenario on attributes ranges (5-12 becomes 5 for the formulas). This allows you to realistically improve your Scouting possibilities.
- **Interested players** -> The third one is a little smaller because it has only a few columns. Using the view *Python - IDs.fmf*, extract a list similar like the ones above but filtering for interested players. The important thing here is getting the UIDs and this will be used to create a binary column later on.
- **Genie Scout** -> The file *Genie View.glf* is a custom view for Genie Scout. You just have to load the game into it and, while you are still at the FM Player Search screen, import all these players into the Genie Scout screen. Then export the data to CSV using the custom view columns.

The export you get from this is named like DEC23 for December 2023 data. This is ready to analyze if you want to go early on and if you have a season full of data this could be a good idea. I tend to start my save games in May 2023 so I have a season worth of data to analyze before even choosing a team. But the best part here is that you can aggregate this exports (JUN23, DEC23, JUN24...) into a single one. This way you only have one line for each player with his total stats up until then and his latest attributes composition.

## Aggregating data
The key file here is *Exports aggregator.ipynb* because it does the exact same as described above. You just set which files the script should combine and run it. This creates a beautiful CSV file consisting in the aggregation of all data. Now you may have even more than a season worth of stats for each player, something that is not possible to easily see in-game.