import discord
import json
import time
from discord.ext import commands
from discord.utils import get
from discord.utils import find
from discord.abc import Messageable

from bot.utils.course import add_course_to_bac, delete_course
from bot.utils.emoji import get_roles, get_key
from bot.utils.setup import setup_bot

bot = commands.Bot(command_prefix='!')
botName = "Info_BOT#8081"


jeton = 'Token'# do not show to anyone

messages = [] # list of all message writen by the bots, in every server

"""
When the bot join a server
"""
@bot.event
async def on_guild_join(guild):
    general = find(lambda x: x.name == 'général',  guild.text_channels)

    if general and general.permissions_for(guild.me).send_messages:
        await general.send('Hello {}!'.format(guild.name))

    await setup_bot(guild, messages)

with open('../data/messages.json', 'r') as infile:
    messages = json.load(infile)

print("Lancement du bot ...")

"""
Launch the bot
"""
@bot.event
async def on_ready():
    for guild in bot.guilds:
        await setup_bot(guild, messages)

    print("bot pret")
    await bot.change_presence(status=discord.Status.idle, activity=discord.Game("la guitare avec Donnet"))

"""
When a reaction is add to the message,
    the user get the role chosen
"""
@bot.event
async def on_raw_reaction_add(payload):
    message_id = payload.message_id
    emoji = payload.emoji.name
    channel = bot.get_channel(payload.channel_id)
    member = bot.get_guild(payload.guild_id).get_member(payload.user_id)

    if str(member) != botName:
        try:
            if message_id in messages:
                if channel.name == "bac-1-choix-cours" or channel.name == "bac-2-choix-cours" or channel.name == "bac-3-choix-cours":
                    message = await Messageable.fetch_message(channel, message_id)
                    content = message.content
                    content = content.replace("\n", "").split(" ")
                    await member.add_roles(get(bot.get_guild(payload.guild_id).roles, name=get_roles((emoji, content[0].upper()))))

                else:
                    await member.add_roles(get(bot.get_guild(payload.guild_id).roles, name=get_roles(emoji)))

        except discord.Forbidden:
            print("Mettre les roles bac{1,2,3} en dessous de celui du bot")

        except discord.HTTPException:
            print("Erreur dans l'ajout des roles")

"""
When a reaction is remove from a message,
    the user loose the role chosen
"""
@bot.event
async def on_raw_reaction_remove(payload):
    message_id = payload.message_id
    emoji = payload.emoji.name
    channel = bot.get_channel(payload.channel_id)
    member = bot.get_guild(payload.guild_id).get_member(payload.user_id)

    try:
        if message_id in messages :
            if channel.name == "bac-1-choix-cours" or channel.name == "bac-2-choix-cours" or channel.name == "bac-3-choix-cours":
                message = await Messageable.fetch_message(channel, message_id)
                content = message.content
                quadri = content.split(" ")
                await member.remove_roles(get(bot.get_guild(payload.guild_id).roles, name=get_roles((emoji, quadri[0].upper()))))

            else:
                await member.remove_roles(get(bot.get_guild(payload.guild_id).roles, name=get_roles(emoji)))

    except discord.NotFound:
        print("Le message n'existe pas")
    except discord.Forbidden:
        print("Erreur de permission")
    except discord.Forbidden:
        print("Mettre les roles bac{1,2,3} en dessous de celui du bot")

"""
restart the bot
"""
@commands.has_role("admin")
@bot.command()
async def restart(ctx):
    await setup_bot(ctx.guild, messages)


"""
Add a new course to a categories
should be use like :
 !add_course {bac} {code} {emoji} {cours}

     example : !add_course B1Q1 MATH2007 :grinning: Mathématiques générales
"""
@commands.has_role("admin")
@bot.command()
async def add_course(ctx):
    msg = str(ctx.message.content).split(maxsplit=4)
    if len(msg) < 5:
        await ctx.channel.send("ERREUR: Le message doit etre composé de \"!add_course {bac} {code} {emoji} {cours}\"")
        raise IOError("Le message doit etre composé de \"!add_course {bac} {code} {emoji} {cours}\"")

    if get_key(msg[2]) is None and get(ctx.guild.text_channels, name=msg[4].lower().replace(" ", "-")) is None:
        await add_course_to_bac(ctx.guild, msg[1], msg[4], msg[2], msg[3])
        quadri = msg[1]

        text_channel = None

        if quadri == "B1Q1" or quadri == "B1Q2":
            text_channel = get(ctx.guild.text_channels, name="bac-1" + "-choix-cours")
        elif quadri == "B2Q1" or quadri == "B2Q2":
            text_channel = get(ctx.guild.text_channels, name="bac-2" + "-choix-cours")
        elif quadri == "B3Q1" or quadri == "B3Q2":
            text_channel = get(ctx.guild.text_channels, name="bac-3" + "-choix-cours")
        else:
            await ctx.channel.send("ERREUR: Le message doit etre composé de \"!add_course {bac} {code} {emoji} {cours}\"")
            raise IOError("Le message doit etre composé de \"!add_course {bac} {code} {emoji} {cours}\"")

        i = 0
        quad = int(quadri[3])
        async for message in text_channel.history(limit=3):
            # nb == 2 and i == 0 corresponds au bac 2, et (nb == 1 and i == 2) au bac 1
            if (quad == 2 and i == 0) or (quad == 1 and i == 2):
                await message.edit(content=message.content + "\n" + msg[3] + " = " + msg[4])
                await message.add_reaction(msg[3])

            i += 1

    else:
        await ctx.send("cours déjà existant")
        print("cours déjà existant")

@commands.has_role("admin")
@bot.command()
async def del_course(ctx):
    guild = ctx.guild
    channel = ctx.channel
    msg = str(ctx.message.content).split(maxsplit=2)
    if get(guild.roles, name=msg[1]) is None:
        await channel.send("Ce cours n'existe pas")
        return

    ok = '👍'
    pasOk = '👎'
    confirmation = await channel.send("Etes vous sur de vouloir supprimé le channel ?")
    await confirmation.add_reaction(ok)
    await confirmation.add_reaction(pasOk)

    def check(reaction, user):
        return (reaction.emoji == ok and reaction.message.id == confirmation.id and reaction.count > 1) or (reaction.emoji == pasOk and reaction.message.id == confirmation.id and reaction.count > 1)

    reaction, user = await bot.wait_for('reaction_add', check=check)
    await confirmation.delete()

    await channel.send(reaction)
    if reaction.emoji == ok:
        role = get(guild.roles, name=msg[1])
        await role.delete()
        await delete_course(msg[1], ctx.guild)



bot.run(jeton)
