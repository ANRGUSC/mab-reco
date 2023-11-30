Here are some notes regarding with the files:

1. For the PWA app, everything needed to run the app is inside the "mab-reco-app" folder. You may see there are
   redundant files such as “configuration.yaml", "ContexualMAB.py", "MABInstance.py" in this folder. That's normal
   since in order to run the Flet PWA app, we need to wrap all the required files insie this folder. In case You
   changed any of these files outside the "mab-reco-app" folder (e.g. files with same naming under the "mab-reco" folder),
   be sure to update them in here as well.

2. For the Telegram and Discord bots, please refer the code in "telegram_main.py" and "discord_main.py". These code are
   modified based on the code given by chatGPT to server different needs. If you have any question, you can refer with
   online documents or directly ask chatGPT (this is more efficient).

3. All the code files come with detailed comments so if you ever have any question, please refer to the comments.

4. You can, run everything all at once with a docker image, to do this please take a look with the "docker-compose-swarm.yml"
   and "docker-compose.yml", you can also find how to run the bots and the Flet PWA app in those files.

5. The database used in the current code assumes you are using MongoDB Atlas database, you need to change the database connection
   string with your own in order for it to work. For the discord and telegram bots, you will also need to create your own bot instances
   and update relevant environment variables inside the ".env" file. Again, if you ever have questions, just ask chatGPT about them. That's
   what I did during the code development, and I found it to be very helpful and efficient.