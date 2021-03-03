import discord
import sqlite3

client = discord.Client()


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    channel = client.get_channel(753275801360662640)
    # await channel.send("Hello, I am Ideabot! I am here to log your ideas")


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$ideas'):
        conn = sqlite3.connect('ideas.db')
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS ideas
                            (idea text)''')
        retval = list(c.execute(f'''SELECT * FROM ideas'''))
        ideas = [x[0] for x in retval]
        await message.channel.send(ideas)
        conn.commit()
        conn.close()

    elif message.content.startswith('$clear'):
        conn = sqlite3.connect('ideas.db')
        c = conn.cursor()
        c.execute('''DROP TABLE IF EXISTS ideas''')
        await message.channel.send('cleared')
        conn.commit()
        conn.close()

    elif message.content.startswith('$idea'):
        content = ' '.join(message.content.split(' ')[1:])
        conn = sqlite3.connect('ideas.db')
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS ideas
                    (idea text)''')
        print(content)
        c.execute("SELECT EXISTS(SELECT 1 FROM ideas WHERE idea=?)", (content,))
        exists = c.fetchone()[0]
        print(exists)
        if not exists:
            c.execute(f'''INSERT INTO ideas VALUES(?)''', (content,))
            conn.commit( )
            conn.close( )
            await message.channel.send("That's a pretty good idea!")
        else:
            await message.channel.send("That idea was already taken!")


client.run('')
