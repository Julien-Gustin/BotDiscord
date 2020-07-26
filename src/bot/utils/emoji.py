import pickle

#Dictionnary like : {id: role_name}, id = {:emoji:, (:emoji:, bac)}
emoji_roles = {}

"""
    load_roles
@brief
    load_roles from file to memory
"""
def load_roles():
    global emoji_roles
    with open('../data/roles.json', 'rb') as infile:
        my_pickler = pickle.Unpickler(infile)
        emoji_roles = my_pickler.load()

"""
    role_delete
@brief
    delete a role from the key
@param
    key: the key of the roles
"""
def role_delete(key):
    global emoji_roles
    if key in emoji_roles:
        del emoji_roles[key]

    with open('../data/roles.json', 'wb') as outfile:
        my_pickler = pickle.Pickler(outfile)
        my_pickler.dump(emoji_roles)

"""
    roles_to_dico
@brief
    add a role to the dico, by his key and role_name
@param
    key: the key of the roles
    role_name: the name of the role
"""
async def roles_to_dico(key, role_name):
    global emoji_roles
    emoji_roles[key] = role_name

    with open('../data/roles.json', 'wb') as outfile:
        my_pickler = pickle.Pickler(outfile)
        my_pickler.dump(emoji_roles)

"""
    get_key
@brief
    get the key from the role_name
@param
    role_name: the name of the role
"""
def get_key(role_name):
    global emoji_roles
    for key, id in emoji_roles.items():
        if role_name == id:
            return key
    return None

"""
    get_roles
@brief
    get the role thanks to the key
@param
    key: the key
"""
def get_roles(key):
    global emoji_roles
    return emoji_roles[key]
