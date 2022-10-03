# bot.py
import os

import discord
from discord.ext import tasks
from dotenv import load_dotenv

import requests
import re

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

class MyClient(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # list of discord channel IDs to update nickname in
        self.guild_ids = []
        self.prev_queue = 0

    async def setup_hook(self) -> None:
        # start the task to run in the background
        self.check_for_update.start()

    async def on_ready(self):
        for guild in client.guilds:
            self.guild_ids.append(guild.id)
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')

    async def update_nickname(self, queue, eta):
        if (queue != self.prev_queue):
            for id in self.guild_ids:
                await client.get_guild(id).me.edit(nick=f'Queue: {queue}')
                await client.change_presence(activity=discord.Game(name=f'ETA {eta}'))
                if self.prev_queue == 0:
                    break # Maybe notify @member or a queue watching group about the queue starting.  (will require ping permissions)               
                self.prev_queue = queue

    @tasks.loop(minutes=5)  # task runs every 5 minutes
    async def check_for_update(self):
        url = 'https://multidollar.company/'
        response = requests.get(url)
        if response.status_code == 200:
            queue = re.search('<div>Number in queue: <span class="has-text-danger">([0-9]*)', response.text, re.IGNORECASE).group(1)
            eta = re.search('<div>Blizzard ETA: <span class="has-text-danger">(.*)(?=<\/span>)', response.text, re.IGNORECASE).group(1)
            if queue and eta:
               await self.update_nickname(queue, eta)

    @check_for_update.before_loop
    async def before_my_task(self):
        await self.wait_until_ready()  # wait until the bot logs in


client = MyClient(intents=discord.Intents.default())
client.run(TOKEN)