import discord
from discord.utils import get
from discord.utils import find
import json

from bot.utils.course import get_list_of_courses, load_courses
from bot.utils.emoji import roles_to_dico, load_roles

channel_name = 'accueil'

"""
    setup_bot
@brief
    Setup the bot
    
@param 
    guild: the server
    messages: list of all discord.Message which the server is on
"""
async def setup_bot(guild, messages):
    await create_bac_roles(guild)
    await setup_category_bot(guild, messages)
    load_roles()
    await load_courses(guild)
    await create_bac_categories(guild)
    await add_course_bac_to_categories(guild)
    await arrange(guild)


"""
    setup_channel_bac_bot
@brief
    Setup the channels about the bac

@param 
    guild: the server
    category_name1: "BxQ1", x = {1, 2, 3} is the first quadrimestre of the bac (str)
    category_name2: "BxQ2", x = {1, 2, 3} is the first quadrimestre of the bac (str)
    bac = {"Bac 1", "Bac 2", "Bac 3"}
    messages: list of all discord.Message which the server is on
"""
async def setup_channel_bac_bot(guild, category_name1, category_name2, bac, messages):
    category = get(guild.categories, name="bot")
    role = get(guild.roles, name=bac)
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False, send_messages=False),
        role: discord.PermissionOverwrite(read_messages=True)
    }

    channel = await create_text_channel_to_category(guild, bac+ " choix cours", category, role)
    await channel.edit(overwrites=overwrites)
    message1 = await channel.send(category_name1 +" Choisissez vos cours en cliquant sur l'émoji associé")
    with open('../data/void.png', 'rb') as f:
        picture = discord.File(f)
        await channel.send(file=picture)

    message2 = await channel.send(category_name2 +" Choisissez vos cours en cliquant sur l'émoji associé")

    # Edit the message to be able to interact with it
    for course in get_list_of_courses():
        if course.quadri_bac == category_name1:
            await message1.add_reaction(course.emoji)
            await message1.edit(content = message1.content + "\n" + course.emoji + " = " + course.name )
            messages.append(message1.id)

        elif course.quadri_bac == category_name2:
            await message2.add_reaction(course.emoji)
            await message2.edit(content = message2.content + "\n" + course.emoji + " = " + course.name )
            messages.append(message2.id)

        with open('../data/messages.json', 'w') as outfile:
            json.dump(messages, outfile)

"""
    arrange
@brief
    arrange the position of categories, to be more user-friendly

@param 
    guild: the server
"""
async def arrange(guild):
    await get(guild.categories, name="bot").edit(position=2)
    await get(guild.categories, name="B1Q1").edit(position=3)
    await get(guild.categories, name="B1Q2").edit(position=4)
    await get(guild.categories, name="B2Q1").edit(position=5)
    await get(guild.categories, name="B2Q2").edit(position=6)
    await get(guild.categories, name="B3Q1").edit(position=7)
    await get(guild.categories, name="B3Q2").edit(position=8)

"""
    add_course_bac_to_categories
@brief
    add course to a category if they aren't anymore

@param 
    guild: the server
"""
async def add_course_bac_to_categories(guild):
    for course in get_list_of_courses():
        course_name = course.name
        bac = course.quadri_bac
        code = course.code
        role = get(guild.roles, name=code)
        if get(guild.text_channels, name=course_name.lower().replace(" ", "-")) is None:
            await create_text_channel_to_category(guild, course_name, get(guild.categories, name=bac), role)

"""
    setup_category_bot
@brief
    setup the category 'bot', which user can interact with the messages, such as get a role or loose a role
@param
    guild: the server
    messages: list of all discord.Message which the server is on
"""
async def setup_category_bot(guild, messages):
    # create a channel for the bot if it doesn't exist yet
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=True),
        guild.default_role: discord.PermissionOverwrite(send_messages=False),
    }
    if find(lambda x: x.name == "bot", guild.categories) is None or find(lambda x: x.name == channel_name, guild.text_channels) is None:
        botCategory = await guild.create_category("bot")
        channel = await guild.create_text_channel(name=channel_name, overwrites=overwrites, category=botCategory, reason=None)
        message = await channel.send(
            "Choisissez votre année,\n 1️⃣ = BAC 1 \n 2️⃣ = BAC 2 \n 3️⃣ = BAC 3 \n \n Si vous avez des cours de deux bacs différents choissiez ces deux bacs")
        messages.append(message.id)
        await message.add_reaction("1️⃣")
        await message.add_reaction("2️⃣")
        await message.add_reaction("3️⃣")

        with open('../data/messages.json', 'w') as outfile:
            json.dump(messages, outfile)
        if find(lambda x: x.name == "bac-1-choix-cours", guild.text_channels) is None:
            await setup_channel_bac_bot(guild, "B1Q1", "B1Q2", "Bac 1", messages)

        if find(lambda x: x.name == "bac-2-choix-cours", guild.text_channels) is None:
            await setup_channel_bac_bot(guild, "B2Q1", "B2Q2","Bac 2", messages)

        if find(lambda x: x.name == "bac-3-choix-cours", guild.text_channels) is None:
            await setup_channel_bac_bot(guild, "B3Q1", "B3Q2","Bac 3", messages)

    if find(lambda x: x.name == "backup", guild.categories) is None:
        await guild.create_category("backup")


"""
    create_bac_roles
@brief
    create all the different rpmes possible (which are the different years) {Bac 1, Bac 2, Bac 3}
@param
    guild: the server
"""
async def create_bac_roles(guild):
    roles = guild.roles
    if get(roles, name="Bac 1") is None:
        bac1 = await guild.create_role(name="Bac 1", colour=discord.Colour.gold())
        await roles_to_dico("1️⃣", "Bac 1")
        await create_text_channel_to_category(guild, "général-bac-1", get(guild.categories, name="Salons textuels"), bac1)

    if get(roles, name="Bac 2") is None:
        bac2 = await guild.create_role(name="Bac 2", colour=discord.Colour.orange())
        await roles_to_dico("2️⃣", "Bac 2")
        await create_text_channel_to_category(guild, "général-bac-2", get(guild.categories, name="Salons textuels"), bac2)

    if get(roles, name="Bac 3") is None:
        bac3 = await guild.create_role(name="Bac 3", colour=discord.Colour.red())
        await roles_to_dico("3️⃣", "Bac 3")
        await create_text_channel_to_category(guild, "général-bac-3", get(guild.categories, name="Salons textuels"), bac3)
"""
    create_bac_categories
@brief
    create all the different category possible {B1Q1, B1Q2, B2Q1, B2Q2, B3Q1, B3Q2} if doesn't exist
@param
    guild: the server
"""
async def create_bac_categories(guild):
    if find(lambda x: x.name == "B1Q1", guild.categories) is None:
        await guild.create_category("B1Q1")

    if find(lambda x: x.name == "B1Q2", guild.categories) is None:
        await guild.create_category("B1Q2")

    if find(lambda x: x.name == "B2Q1", guild.categories) is None:
        await guild.create_category("B2Q1")

    if find(lambda x: x.name == "B2Q2", guild.categories) is None:
        await guild.create_category("B2Q2")

    if find(lambda x: x.name == "B3Q1", guild.categories) is None:
        await guild.create_category("B3Q1")

    if find(lambda x: x.name == "B3Q2", guild.categories) is None:
        await guild.create_category("B3Q2")


"""
    create_text_channel_to_category
@brief
    create a text channel, that can only be accessible from role
@param
    guild: the server (discord.guild)
    channel_name: the name of the channel to create (string)
    category: the category of the channel (discord.categories)
    role: role which can access to the channel (discord.roles)
"""
async def create_text_channel_to_category(guild, channel_name, category, role):
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        role: discord.PermissionOverwrite(read_messages=True)
    }
    if get(guild.text_channels, name=channel_name.lower().replace(" ", "-")+"-backup") is not None:
        return await get(guild.text_channels, name=channel_name.lower().replace(" ", "-")+"-backup").edit(category=category, name=channel_name)
    return await guild.create_text_channel(name=channel_name, overwrites=overwrites, category=category, reason=None)




