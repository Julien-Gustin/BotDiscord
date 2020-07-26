import pickle
from discord.utils import get
from bot.utils.emoji import roles_to_dico, role_delete

courses_bac = []

class Course:
    def __init__(self, quadri_bac, name, code, emoji, bac):
        self.code = code
        self.name = name
        self.quadri_bac = quadri_bac
        self.bac = bac
        self.emoji = emoji

    """
        add_roles
    @brief
        keep the course in memory

    @param 
        guild: the server
        
    @return 
        role: the role associated
    """
    async def add_roles(self, guild):
        role = None
        if get(guild.roles, name=self.code) is None:
            role = await guild.create_role(name=self.code)

        await roles_to_dico((self.emoji, self.quadri_bac), self.code)
        return role

    """
        delete
    @brief
        delete the course from anywhere

    @param 
        guild: the server
    """
    async def delete(self, guild):
        text_channel = get(guild.text_channels, name=self.bac.lower()+"-choix-cours".replace(" ", "-"))
        nb = int(self.quadri_bac[3])
        j = 0
        async for message in text_channel.history(limit=3):
            if (nb == 2 and j == 0) or (nb == 1 and j == 2):
                await message.clear_reaction(self.emoji)
                content = message.content
                content = content.split("\n")
                i = 0
                while i < len(content):
                    if content[i][0] == self.emoji[0]:
                        content.pop(i)
                    i += 1

                await message.edit(content='\n'.join(content))
            j += 1

        course_channel = get(guild.text_channels, name=self.name.lower().replace(" ", "-"))
        await course_channel.edit(category=get(guild.categories, name="backup"), name=course_channel.name+"-backup")
        role_delete((self.emoji, self.quadri_bac))
        del self

    """
        get_list_of_courses
    @brief
        return the list of course
    
     @return
        courses_bac
    """
def get_list_of_courses():
    global courses_bac
    return courses_bac

"""
    load_courses
@brief
    load the differents courses from file to memory
"""
async def load_courses(guild):
    with open('../data/courses_bac.json', 'rb') as infile:
        global courses_bac
        my_pickler = pickle.Unpickler(infile)
        courses_bac = my_pickler.load()
        for course in courses_bac:
            await course.add_roles(guild)

"""
    add_course_to_bac
@brief
    add a channel (course) to the correct category
@param
    guild: the server (discord.guild)
    bac_quadri: {B1Q1, B1Q2, B2Q1, B2Q2, B3Q1, B3Q2} (string)
    course_name: the name of the channel (string)
    code: code of the course
"""
async def add_course_to_bac(guild, bac_quadri, course_name, code, emoji):
    global courses_bac
    if bac_quadri.upper() == "B1Q1" or bac_quadri.upper() == "B1Q2":
        course = Course(bac_quadri, course_name, code, emoji, "bac-1")

    elif bac_quadri.upper() =="B2Q1" or bac_quadri.upper() == "B2Q2":
        course = Course(bac_quadri, course_name, code, emoji, "bac-2")

    elif bac_quadri.upper() =="B3Q1" or bac_quadri.upper() == "B3Q2":
        course = Course(bac_quadri, course_name, code, emoji, "bac-3")

    else:
        raise IOError("Le bac_quadri donné n'existe pas")

    role = await course.add_roles(guild)
    courses_bac.append(course)
    with open('../data/courses_bac.json', 'wb') as outfile:
        my_pickler = pickle.Pickler(outfile)
        my_pickler.dump(courses_bac)

    from bot.utils.setup import create_text_channel_to_category
    await create_text_channel_to_category(guild, course_name, get(guild.categories, name=bac_quadri), role)

"""
    delete_course
@brief
    delete a course from anywhere
@param
    guild: the server (discord.guild)
"""
async def delete_course(code, guild):
    global courses_bac
    i = 0

    while i < len(courses_bac):
        if courses_bac[i].code == code:
            await courses_bac[i].delete(guild)
            courses_bac.pop(i)

        i += 1

    with open('../data/courses_bac.json', 'wb') as outfile:
        my_pickler = pickle.Pickler(outfile)
        my_pickler.dump(courses_bac)
