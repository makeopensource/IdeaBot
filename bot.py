import discord
import json
from dotenv import load_dotenv
import os

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
ADD_IDEA, REMOVE_IDEA = os.getenv('ADD_IDEA'), os.getenv('REMOVE_IDEA')
ALL_IDEAS, CLEAR_IDEAS = os.getenv('ALL_IDEAS'), os.getenv('CLEAR_IDEAS')


class MyClient(discord.Client):
    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))

    async def on_message(self, message):
        m = self.parse_message(message.content)
        # if message.content.startswith('$') and m[1] == '':
        #     await message.channel.send('invalid query')

        if m[0] == f'${ADD_IDEA}':
            success = self.store_idea(m[1])
            if success:
                await message.channel.send(f'added {m[1]}')
            else:
                await message.channel.send(f'{m[1]} already exists')

        elif m[0] == f'${ALL_IDEAS}':
            await message.channel.send(self.get_ideas())

        elif m[0] == f'${REMOVE_IDEA}':
            success = self.remove_idea(m[1])
            if success:
                await message.channel.send(f'removed {m[1]}')
            else:
                await message.channel.send(f'{m[1]} does not exist')

        elif m[0] == f'${CLEAR_IDEAS}':
            self.clear_ideas()
            await message.channel.send('cleared all ideas')

    def parse_message(self, message):
        parts = message.split(' ')
        header = parts[0]
        content = ' '.join(parts[1:])
        return [header, content]

    # returns success/failure
    def store_idea(self, idea):
        json_file = open('data.json', 'r')
        data = json.load(json_file)
        if idea not in data:
            data.append(idea)
            json_file = open('data.json', 'w')
            json.dump(data, json_file)
            json_file.close()
            return True
        else:
            json_file.close()
            return False

    def get_ideas(self):
        with open('data.json', 'r') as f:
            data = json.load(f)
            f.close()
            return data

    # returns success/failure
    def remove_idea(self, idea):
        f = open('data.json', 'r')
        data = json.load(f)
        if idea in data:
            data.remove(idea)
            f = open('data.json', 'w')
            json.dump(data, f)
            f.close()
            return True
        else:
            f = open('data.json', 'w')
            json.dump(data, f)
            f.close()
            return False

    # for testing purposes only
    def clear_ideas(self):
        with open('data.json', 'w') as f:
            json.dump([], f)
            f.close()


client = MyClient()
client.run(TOKEN)
