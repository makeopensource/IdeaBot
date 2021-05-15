import discord
from discord.ext import commands
from discord_slash import SlashCommand, SlashContext
from dotenv import load_dotenv
import os
from pymongo import MongoClient

# initializers
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
TICKER = os.getenv('CALL_SYMBOL')
DB_ADDRESS = os.getenv('DB_ADDRESS')
DESCRIPTION = os.getenv("DESCRIPTION")
COMMAND_PREFIX = os.getenv("COMMAND_PREFIX")
GUILD_IDS = [int(os.getenv("GUILD_IDS",0))]

intents = discord.Intents.all()
intents.members = True

bot = commands.Bot(command_prefix=COMMAND_PREFIX, description=DESCRIPTION,intents=intents)
slash = SlashCommand(bot,sync_commands=True)

# database manipulation definitions
class InvalidAccess(Exception):
    """You do not have write permissions for this idea"""
    pass

def insertIdea(idea, author, contributors, github, author_id):
    with MongoClient(DB_ADDRESS) as db_client:
        idea_db = db_client.test
        ideas = idea_db.ideas
        idea1 = {
                "idea": idea,
                "author": author,
                "authorID": author_id,
                "contributors": contributors,
                "github": github
                }
        existing = ideas.find_one({"idea": idea})
        if existing is not None and existing["authorID"] != author_id:
            raise InvalidAccess
        elif existing is not None:
            ideas.replace_one({"idea": idea}, idea1)
        else:
            ideas.insert_one(idea1)

def allIdeas():
    with MongoClient(DB_ADDRESS) as db_client:
        idea_db = db_client.test
        ideas = idea_db.ideas
        return ideas.find()

def removeIdea(idea, author_id):
    with MongoClient(DB_ADDRESS) as db_client:
        idea_db = db_client.test
        ideas = idea_db.ideas
        existing = ideas.find_one({"idea": idea})
        if existing is not None and existing["authorID"] == author_id:
            ideas.remove({"idea": idea})
        else:
            raise InvalidAccess

# bot commands and initialization

@bot.event
async def on_ready():
    print("logged in as " + bot.user.name)

@slash.slash(name="help",description="Help Command",guild_ids=GUILD_IDS)
async def help(ctx: SlashContext):
    embed = discord.Embed(title="Help")
    embed.add_field(name="$add [idea], [author]", value="add an idea", inline=True)
    embed.add_field(name="$edit [idea], [author]", value="edit an idea", inline=True)
    embed.add_field(name="$remove [idea]", value="remove an idea (only available to idea author and admins)",inline=False)
    await ctx.send(embed=embed)

@slash.slash(name="add",description="Add an idea",guild_ids=GUILD_IDS)
async def add(ctx: SlashContext):
    insertIdea(ctx.message,ctx.author,[],"",ctx.author_id)
    await ctx.send(content=(f"{ctx.author} sucessfully added {ctx.message}"))

@slash.slash(name="add",description="Add an idea",guild_ids=GUILD_IDS)
async def edit(ctx: SlashContext):
    insertIdea(ctx.message,ctx.author,[],"",ctx.author_id)
    await ctx.send(content=(f"{ctx.author} sucessfully edited {ctx.message}"))

@slash.slash(name="all",description="List All Ideas",guild_ids=GUILD_IDS)
async def all(ctx: SlashContext):
    await ctx.send(content=allIdeas())

@slash.slash(name="remove",description="Remove an idea")
async def remove(ctx: SlashContext):
    removeIdea(ctx.message,ctx.author_id)
    await ctx.send(content=f"Idea {ctx.message} removed")

bot.run(TOKEN)
