import discord
from discord.ext import commands
from discord_slash import SlashCommand, SlashContext
from discord_slash.model import SlashCommandOptionType
from discord_slash.utils.manage_commands import create_option

import datetime
from dotenv import load_dotenv
import os
import requests

# initializers
load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
IDEA_TOKEN = os.getenv('IDEA_TOKEN')
BASE_URL = os.getenv('BASE_URL')  # root URL for requests (including '/' at end)
GUILD_IDS = [int(os.getenv('GUILD_IDS',0))]

head = {'Authorization': 'Token ' + IDEA_TOKEN}

intents = discord.Intents.all()
intents.members = True

bot = commands.Bot(command_prefix="!", description=DESCRIPTION,intents=intents)
slash = SlashCommand(bot,sync_commands=True)



###################################
# database manipulation functions #
###################################

class InvalidAccess(Exception):
    """You do not have write permissions for this idea"""
    pass

def insertIdea(title, description, author):
    new_idea = {
        'title': title,
        'description': description,
        'author': author,
        'approved': False
    }
    idea = requests.get(
        f"{BASE_URL}idealab/ideas/?title={title.replace(' ', '%20')}",
        headers=head
    ).json()
    if idea['count'] != 0:
        raise InvalidAccess
    # check for updates here
    else:
        response = requests.post(url=f'{BASE_URL}idealab/ideas/',
                                 json=new_idea, headers=head)
        return(response)


def allIdeas():
    idea = requests.get(f"{BASE_URL}idealab/ideas/").text
    return idea


def removeIdea(title):
    response = requests.delete(
        f"{BASE_URL}idealab/ideas/?title={title.replace(' ', '%20')}",
        headers=head)
    return response.status_code


###################################
# bot commands and initialization #
###################################

@bot.event
async def on_ready():
    print('logged in as ' + str(bot.user.name))


@slash.slash(name="help", description='Help Command', guild_ids=GUILD_IDS)
async def help(ctx: SlashContext):
    embed = discord.Embed(title='Help')
    embed.add_field(name='$add [idea]', value='add an idea', inline=True)
    embed.add_field(name='$edit [idea]', value='edit an idea', inline=True)
    embed.add_field(name='$remove [idea]', value='remove an idea (only available to idea author and admins)', inline=False)
    await ctx.send(embed=embed)

@slash.slash(name='add',
            description='Add an idea',
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
    insertIdea(title, description, name)
    await ctx.send(content=(f'{name} sucessfully added "{title}"'))

@slash.slash(name='edit',
            description='Edit an idea',
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
    insertIdea(title, description, name)
    await ctx.send(content=(f'{ctx.author.nick} sucessfully edited "{title}"'))

@slash.slash(name='all', description='List All Ideas', guild_ids=GUILD_IDS)
async def all(ctx: SlashContext):
    await ctx.send(content=allIdeas())

@slash.slash(name='remove',
            description='Remove an idea',
            options=[
                create_option(
                    name='title',
                    description='the title of your idea',
                    option_type=SlashCommandOptionType.STRING,
                    required=True
                ),
            ])
async def remove(ctx: SlashContext, title: str):
    response = removeIdea(title)
    if response == 200:
        await ctx.send(content=f'Idea "{title}" removed')
    else:
        await ctx.send(content='Error' + response)

bot.run(DISCORD_TOKEN)
