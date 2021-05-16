import discord
from discord.ext import commands
from discord_slash import SlashCommand, SlashContext

from discord_slash.model import SlashCommandOptionType
from discord_slash.utils.manage_commands import create_option

import datetime

from dotenv import load_dotenv
import os

from pymongo import MongoClient

# initializers
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
DB_ADDRESS = os.getenv('DB_ADDRESS')
DB_NAME = os.getenv('DB_NAME')
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

def insertIdea(title, description, author, author_id):
    with MongoClient(DB_ADDRESS) as db_client:
        idea_db = db_client.DB_NAME
        ideas = idea_db.ideas
        new_idea = {
            "title": title,
            "description": description,
            "author": author,
            "author_id": author_id,
            "release_date": datetime.date.today,
            "approved": False,
        }
        existing = ideas.find_one({"title": title})
        if existing is not None and existing["author_id"] != author_id:
            raise InvalidAccess
        elif existing is not None:
            ideas.replace_one({"title": title}, new_idea)
        else:
            ideas.insert_one(new_idea)

def allIdeas():
    with MongoClient(DB_ADDRESS) as db_client:
        idea_db = db_client.DB_NAME
        ideas = idea_db.ideas
        return str(list(ideas.find()))

def removeIdea(title, author_id):
    with MongoClient(DB_ADDRESS) as db_client:
        idea_db = db_client.DB_NAME
        ideas = idea_db.ideas
        existing = ideas.find_one({"title": title})
        if existing is not None and existing["author_id"] == author_id:
            ideas.remove({"title": title})
        else:
            raise InvalidAccess

# bot commands and initialization

@bot.event
async def on_ready():
    print("logged in as " + bot.user.name)

@slash.slash(name="help", description="Help Command", guild_ids=GUILD_IDS)
async def help(ctx: SlashContext):
    embed = discord.Embed(title="Help")
    embed.add_field(name="$add [idea]", value="add an idea", inline=True)
    embed.add_field(name="$edit [idea]", value="edit an idea", inline=True)
    embed.add_field(name="$remove [idea]", value="remove an idea (only available to idea author and admins)",inline=False)
    await ctx.send(embed=embed)

@slash.slash(name="add",
            description="Add an idea",
            guild_ids=GUILD_IDS,
            options=[
                create_option(
                    name='title',
                    description='the title of your idea',
                    option_type=SlashCommandOptionType.STRING,
                    required=True
                ),
                create_option(
                    name='description',
                    description='a description of your idea',
                    option_type=SlashCommandOptionType.STRING,
                    required=True
                ),
                create_option(
                    name='name',
                    description='your name',
                    option_type=SlashCommandOptionType.STRING,
                    required=True
                ),
            ])
async def add(ctx: SlashContext, title: str, description: str, name: str):
    insertIdea(title, description, name, ctx.author_id)
    await ctx.send(content=(f"{name} sucessfully added {title}"))

@slash.slash(name="edit",
            description="Edit an idea",
            guild_ids=GUILD_IDS,
            options=[
                create_option(
                    name='title',
                    description='the title of your idea',
                    option_type=SlashCommandOptionType.STRING,
                    required=True
                ),
            ])
async def edit(ctx: SlashContext, title: str, description: str, name: str):
    insertIdea(title, description, name, ctx.author_id)
    await ctx.send(content=(f"{ctx.author} sucessfully edited {ctx.message}"))

@slash.slash(name="all", description="List All Ideas", guild_ids=GUILD_IDS)
async def all(ctx: SlashContext):
    await ctx.send(content=allIdeas())

@slash.slash(name="remove",
            description="Remove an idea",
            options=[
                create_option(
                    name='title',
                    description='the title of your idea',
                    option_type=SlashCommandOptionType.STRING,
                    required=True
                ),
            ])
async def remove(ctx: SlashContext, title: str):
    removeIdea(title, ctx.author_id)
    await ctx.send(content=f"Idea {title} removed")

bot.run(TOKEN)
