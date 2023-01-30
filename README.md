# IsPlayerOnlineGraph
Tools to ping a Minecraft server for the names of online players and save it to a database, and **plot a timeline graph of online players over time**.

Helps server members **determine the playing schedule** of an elusive player they wish to interact with, useful for competitive and content-creation server playstyles. Also helps players seeking interaction to **align their playtime to the most busy part of the day**.

WARNING: Your IP address is exposed to the server whenever you ping it using the __main__.py script. While this does not appear in console.log, server admins may be able to see this information. Use a VPN.

### Components:
- main.py uses the [mcstatus python library](https://github.com/py-mine/mcstatus) to make a Status API call to the server using the [Server List Ping Protocol](https://wiki.vg/Server_List_Ping) to retrieve online players. This is the same information that a Minecraft client gets when to show data on the Multiplayer screen.
- Timestamp in UTC, Player name, and whether the server is contactable is logged in a time series MongoDB Atlas Database
- app.py pulls data from the MongoDB databse, and plots a Plotly timeline within a dash webapp. 

Requirements:
- Tested in python 3.10
- MongoDB >= 5.0 (timeseries feature is used)

Visualisation Placeholder (Screenshot of actual graph coming soon):
![](https://linuxhint.com/wp-content/uploads/2022/08/Plotly.Express.Timeline-4.png)

### How to use:
- Tested in python 3.10
- Install required libraries. You may wish to use zipapp to create a .pyz archive
- Create a MongoDB database on Atlas. **Fill in the variables for the database access, database name and collection** at the top of the scripts
- Run a cron job every 5 minutes. The script extrapolate the presence of a player to the next 5th minute. You may wish to use cronitor to track the cron job
- Run the dash webapp to view the plot

