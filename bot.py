import discord
from dotenv import load_dotenv
import os
from pymongo import MongoClient


# initializers
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
DB_PASSWORD = os.getenv('DB_PASSWORD')
address = f"mongodb+srv://emilkovacev:{DB_PASSWORD}@cluster0.aryp3.mongodb.net/ideas?retryWrites=true&w=majority"


# custom exceptions
class InvalidAccess(Exception):
    """You do not have write permissions for this Idea"""
    pass


class MyClient(discord.Client):
    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))

    async def on_message(self, message):
        parsed = self.parse_message(message.content)
        if parsed[0] == '$add' or parsed[0] == '$edit':
            idea = parsed[1]
            author = parsed[2]
            self.insert_idea(idea, author, [], "", message.author.id)
            await message.channel.send(f'{message.author.nick} successfully {parsed[0][1:]}ed {idea}')
        elif parsed[0] == '$all':
            return self.all_ideas()
        elif parsed[0] == '$remove':
            pass

    @classmethod
    def parse_message(self, content):
        content = content.replace(' ', ', ', 1)
        return content.split(", ")

    @classmethod
    def insert_idea(self, idea, author, contributors, github, author_id):
        with MongoClient(address) as db_client:
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
        with MongoClient(address) as db_client:
            idea_db = db_client.test
            ideas = idea_db.ideas
            return ideas.find()


client = MyClient()
client.run(TOKEN)
