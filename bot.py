import discord
from dotenv import load_dotenv
import os
from pymongo import MongoClient


# initializers
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
TICKER = os.getenv('CALL_SYMBOL')
DB_ADDRESS = os.getenv('DB_ADDRESS')


# custom exceptions
class InvalidAccess(Exception):
    """You do not have write permissions for this idea"""
    pass


class MyClient(discord.Client):
    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))

    async def on_message(self, message):
        parsed = self.parse_message(message.content)

        if parsed[0] == f'{TICKER}help':
            embed = discord.Embed(title="Help")
            embed.add_field(name="$add [idea], [author]", value="add an idea", inline=True)
            embed.add_field(name="$edit [idea], [author]", value="edit an idea", inline=True)
            embed.add_field(name="$remove [idea]", value="remove an idea (only available to idea author and admins)",inline=False)
            await message.channel.send(embed=embed)
        elif parsed[0] == f'{TICKER}add' or parsed[0] == f'{TICKER}edit':
            idea = parsed[1]
            author = parsed[2]
            self.insert_idea(idea, author, [], "", message.author.id)
            await message.channel.send(f'{message.author.nick} successfully {parsed[0][1:]}ed {idea}')

        elif parsed[0] == f'{TICKER}all':
            return self.all_ideas()

        elif parsed[0] == f'{TICKER}remove':
            idea = parsed[1]
            self.remove_idea(idea, message.author.id)

    @classmethod
    def parse_message(self, content):
        content = content.replace(' ', ', ', 1)
        return content.split(", ")

    @classmethod
    def insert_idea(self, idea, author, contributors, github, author_id):
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

    @classmethod
    def all_ideas(self):
        with MongoClient(DB_ADDRESS) as db_client:
            idea_db = db_client.test
            ideas = idea_db.ideas
            return ideas.find()

    @classmethod
    def remove_idea(self, idea, author_id):
        with MongoClient(DB_ADDRESS) as db_client:
            idea_db = db_client.test
            ideas = idea_db.ideas
            existing = ideas.find_one({"idea": idea})
            if existing is not None and existing["authorID"] == author_id:
                ideas.remove({"idea": idea})
            else:
                raise InvalidAccess


client = MyClient()
client.run(TOKEN)
