import discord
import sqlite3
import datetime
import json

intents = discord.Intents.default()
intents.message_content = True

activity = discord.Activity(type=discord.ActivityType.watching, name="the world burn")
client = discord.Client(intents=intents, activity=activity)

# brimstone database
brimstone_db = sqlite3.connect("brimstone.db")
cur = brimstone_db.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS brimstone(id INTEGER PRIMARY KEY)")

coals_this_session = 0

#configs
with open('config.json', 'r') as file:
    config = json.load(file)
    bot_token = str(config['token'])
    brimstone_threshold = int(config['threshold'])
    coal_emoji = str(config['coal'])
    config_timeout = config['timeout']
    

async def insert_brimstone(message_id):
    cur.execute("""
        INSERT INTO brimstone VALUES
        (?)
        """, (message_id,))
    brimstone_db.commit()
    return

async def get_is_already_brimstone(message_id):
    res = cur.execute("SELECT id FROM brimstone WHERE id = (?)", (message_id,))
    return not res.fetchone() is None
    

@client.event
async def on_ready():
    print(f'logged in as {client.user}')
        
@client.event
async def on_reaction_add(reaction, user):
    message = reaction.message
    print(reaction.emoji.id)
    if message.author == client.user:
        return
    
    if not str(reaction.emoji.id) == coal_emoji:
        return
        
    # brimstone doesnt stack
    if await get_is_already_brimstone(message.id):
        return
    
    if reaction.count >= brimstone_threshold:
        member = reaction.message.author
        try:
            await member.timeout(datetime.timedelta(seconds=int(config_timeout['seconds']),minutes=int(config_timeout['minutes']), hours=int(config_timeout['hours'])), reason="coalposting")
        except discord.errors.Forbidden:
            await message.reply(f'can\'t time out moderators for coalposting', mention_author=False)
            await insert_brimstone(message.id)
            return
        await message.reply(f'timed out {member.mention} for coalposting', mention_author=False)
        await insert_brimstone(message.id)
        return
        

client.run(bot_token)