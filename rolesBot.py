import discord
from discord.ext import commands
import os
import sys

# Global variables
client = commands.Bot(command_prefix='!')
membersRole = None
coreRole = None


# Searches through an array of roles for the role with the matching name
def find_role_index(content, role_list):
    for i in range(len(role_list)):
        curr_role = role_list[i]

        if content.lower() == curr_role.name.lower():
            return i

    return -1


# checks if the user has the role "member"
def has_member(author):
    global membersRole
    for i in range(len(author.roles)):
        if author.roles[i] == membersRole:
            return True

    return False


# Checks if the given author has coreRole
def has_core(author):
    global coreRole

    for i in range(len(author.roles)):
        if author.roles[i].position >= coreRole.position:
            return True

    return False


# Tries to add the author to the given role
@client.event
async def add_role(author, channel, content):
    server_roles = author.server.roles

    content = list(content)

    outp = ""
    joined_roles = ""
    misnamed_roles = ""
    already_in_roles = ""
    forbidden_roles = ""

    if len(content) > 3:
        await client.send_message(channel, "Joining many roles at once may take a few moments")

    for i in content:
        i = i.lstrip()
        index = find_role_index(i, server_roles)

        # Checks to see if role exists
        if index > 0:
            curr_role = server_roles[index]

            # This section checks to see if the author is already in the requested role
            if find_role_index(curr_role.name, author.roles) == -1:

                try:
                    while find_role_index(curr_role.name, author.roles) == -1:
                        await client.add_roles(author, curr_role)
                    joined_roles += curr_role.name + ", "
                    print(author.name + " joined the role")

                except discord.errors.Forbidden:
                    forbidden_roles += curr_role.name + ", "
                    print(author.name + " tried to join a restricted role (bot permissions too low)")

            else:
                print(author.name + " was already in that role")
                already_in_roles += curr_role.name + ", "

        else:
            misnamed_roles += i + ", "
            print("Role does not exist")

    if len(joined_roles) > 0:
        outp += "Successfully joined " + joined_roles[:-2] + "\n"
    if len(misnamed_roles) > 0:
        outp += misnamed_roles[:-2] + " role(s) do not exist\n"
    if len(already_in_roles) > 0:
        outp += "You are already in " + already_in_roles[:-2] + "\n"
    if len(forbidden_roles) > 0:
        outp += "Locked/ unjoinable roles: " + forbidden_roles[:-2] + "\n"

    await client.send_message(channel, outp)

# detects when bot is ready
@client.event
async def on_ready():
    global membersRole, serverID, coreRole

    get_server = client.get_server(serverID)

    if get_server is None:
        print("Invalid server ID:" + str(serverID))
        await client.close()
        sys.exit()

    server_roles = get_server.roles

    # Finds members and core roles
    membersRole = find_role_index("members", server_roles)
    coreRole = find_role_index("core", server_roles)

    if membersRole != -1:
        membersRole = server_roles[membersRole]
        coreRole = server_roles[coreRole]
        print('Members and Core roles configured')
    else:
        print("Failed to configured members role!")
        sys.exit(0)

    if len(client.get_server(serverID).me.roles) > 2:
        print("Bot should only be in one role (The bot role)")
        sys.exit(0)

    # Checks to see if the bot has a role of Bot
    if find_role_index("bot", client.get_server(serverID).me.roles) != -1:
        print("Bot is in proper role")
    else:
        print("Bot needs to be in role \"Bot\"")
        sys.exit(0)

    print('Bot is online and active')


# Use on_message so the bot runs on every message sent. Also checks if certain commands were entered
@client.event
async def on_message(message):
    global membersRole, coreRole
    whole_string = message.content.split()
    command = whole_string[0]
    command = command.lower()

    # gets discord objects so the bot can use them as needed
    author = message.author
    channel = message.channel
    server = message.server

    if command[0] == '!':

        if has_member(author):

            # Gets the users "message" (ignores command prefix ie: "!join")
            del whole_string[0]
            content = ' '.join(whole_string)
            content = content.lower()

            # User commands below
            # ----------------------------------------------------------------------------------------

            # Tries to give the author user the specified role
            if command == "!join":
                print("\nAttempting to give " + author.name + " a role: " + content)

                # checks if user gave an argument
                if len(content) > 0:

                    # Assigns user all available roles
                    if content == "all":
                        server_roles = channel.server.roles
                        joinable = []
                        for i in range(len(server_roles)):
                            bot_role_index = find_role_index("bot", message.server.me.roles)

                            curr_role = server_roles[i]
                            if ((i > 0 and curr_role.position < message.server.me.roles[bot_role_index].position) and (
                                    curr_role != membersRole)):
                                joinable.append(curr_role.name)

                        await add_role(author, channel, joinable)
                        print("gave " + author.name + " all available roles")
                    else:
                        content = content.split(',')
                        await add_role(author, channel, content)

                else:
                    await client.send_message(channel, "Must provide at least one argument")
                    print(author.name + " used join without arguments")

            # Tries to remove the author from a specified role
            elif command == "!leave":
                print("\n" + author.name + " wants to leave a role: " + content)

                if len(content) > 0:
                    author_roles = author.roles
                    mem = membersRole.name

                    if content != mem:
                        index = find_role_index(content, author_roles)
                        if index > 0:
                            try:
                                await client.remove_roles(author, author_roles[index])
                                await client.send_message(channel, "You are no longer in " + author_roles[index].name)
                                print(author.name + " left " + author_roles[index].name)
                            except discord.errors.Forbidden:
                                print("Bot does not have permission to remove role")
                                await client.send_message(channel, "I cannot remove you from this role")
                        else:
                            await client.send_message(channel,
                                                      "You have no role \"" + content + "\" maybe you misspelled it?")
                            print(author.name + " is not in that role")
                    else:
                        print("User tried to leave members role")
                        await client.send_message(channel,
                                                  "Cannot leave members role. If you want to leave member role ask a "
                                                  "team leader or admin to remove you")

                else:
                    print("user did not provide argument")
                    await client.send_message(channel, "Must provide at least one argument")
            # lists roles joinable by all members
            elif command == "!listroles":
                print("\n" + author.name + " requested a list of roles")
                server_roles = channel.server.roles
                outp = "**Server Roles:**\n"

                for i in range(len(server_roles)):
                    bot_role_index = find_role_index("bot", message.server.me.roles)
                    curr_role = server_roles[i]
                    if ((i > 0 and curr_role.position < message.server.me.roles[bot_role_index].position) and (
                            curr_role != membersRole)):
                        outp += "\t" + curr_role.name + "\n"

                await client.send_message(channel, outp)

            elif (command == "!listunjoined" or command == "!listunjoinedroles" or command == "!listjoinable"
                  or command == "!listjoinableroles" or command == "!unjoinedroles"):
                print("\n" + author.name + " requested a list of unjoined roles")
                server_roles = channel.server.roles
                outp = "**Unjoined Roles:**\n"

                for i in range(len(server_roles)):
                    bot_role_index = find_role_index("bot", message.server.me.roles)
                    curr_role = server_roles[i]
                    if (i > 0 and find_role_index(curr_role.name, author.roles) == -1 and curr_role.position <
                            message.server.me.roles[bot_role_index].position) and (curr_role != membersRole):
                        outp += "\t" + curr_role.name + "\n"
                if len(outp) > 20:
                    await client.send_message(channel, outp)
                else:
                    await client.send_message(channel, "You are already in all joinable roles")

            # Lists the roles of a user
            elif command == "!myroles" or command == "!getroles" or command == "!getrole" or command == "!myrole":
                print("\n" + author.name + " requested the roles of a user")

                user_roles = None
                name = None
                outp = ""

                # If a name is given to check
                if len(content) > 0:

                    if len(message.mentions) > 0:
                        name = message.mentions[0].name
                        user_roles = message.mentions[0].roles
                    else:
                        # loops through all members in the server to find input name
                        for i in range(len(server.members)):

                            curr_member = list(server.members)
                            curr_member = curr_member[i]

                            if content == curr_member.name.lower() or content == curr_member.display_name.lower() or \
                                    content == curr_member.id.lower():
                                name = curr_member.name
                                user_roles = curr_member.roles
                                break

                # in no input is given
                else:
                    user_roles = author.roles
                    name = author.name

                # if user is found
                if name is not None and user_roles is not None:
                    outp += "**" + name + "\'s Roles:**\n"

                    for i in range(len(user_roles)):
                        if i > 0:
                            outp += "\t" + str(i) + ". " + user_roles[i].name + "\n"

                    await client.send_message(channel, outp)
                    print("Showing roles for " + name)

                # If the name is not in the server
                else:
                    print(author.name + " did not provide a valid argument")
                    await client.send_message(channel, "Cannot find that user. check spelling")

            # adds all mentioned (@name) users to the members role
            elif command == "!addmembers" or command == "!addmember":
                print("\n" + author.name + " is trying to add a new member")
                outp = ''

                # if the author has permission to issue this command
                if has_core(author):

                    added_new_member = False
                    for i in range(len(message.mentions)):

                        curr_person = message.mentions[i]
                        # if the user isn't already in the members role
                        if has_member(curr_person) is False:
                            print("new member " + curr_person.name + " added")
                            await client.add_roles(curr_person, membersRole)
                            added_new_member = True
                            outp += "Welcome " + curr_person.mention + " to the USCRPL server " + '\n'
                        else:
                            print(curr_person.name + " is already in the members role")

                    if added_new_member is True:
                        outp += "When you are ready use !listRoles for a list of the joinable roles. Then use !join (" \
                                "role) to view the different text channels"
                else:
                    print(author.name + " doesnt have permission to add member")
                    outp = "You don't have permission to add member"

                # sends all updates as one message to prevent delay
                await client.send_message(channel, outp)

                # Tries to message in all text channels. If the bot can message in a channel it is not supposed to then
                # that channel is vulnerable
            elif command == "!tc" or command == "!testchannels":

                print("\n" + author.name + " is testing channel security")
                if has_core(author):

                    all_secure = True
                    count = 0
                    channels = list(server.channels)

                    await client.send_message(channel,
                                              "Testing all text channels for vulnerability, this will take a few "
                                              "moments")

                    # This can actually be made more efficient by checking permissions before trying to send a
                    # message (sending a message has lag)
                    for i in range(len(channels)):
                        if channels[i].type == discord.ChannelType.text and channels[i] != channel:
                            try:
                                await client.send_message(channels[i], author.mention)
                                print(channels[i].name + " can be accessed and messaged by bot")
                                all_secure = False
                            except discord.errors.Forbidden:
                                count += 1

                    if all_secure:
                        print("All channels secure")
                        await client.send_message(channel, "Done")
                    else:
                        await client.send_message(channel,
                                                  "Done. You have been pinged in all channels the bot can access")

                else:
                    print(author.name + " doesnt have permission to test channels")
                    await client.send_message(channel, "You need to be a core member to use this command")

            # Lists all users who are not in the members role
            elif command == "!nonmembers" or command == "!nonmember":
                print("Listing nonmembers")
                has_nonmember = False
                outp = "**Non members:** \n"
                for i in author.server.members:
                    memb = False
                    for j in i.roles:
                        if j.name.lower() == "member" or j.name.lower() == "members":
                            memb = True
                            break
                    if not memb and not i.bot:
                        has_nonmember = True
                        outp += i.display_name + ","

                if has_nonmember:
                    await client.send_message(channel, outp)
                else:
                    await client.send_message(channel, "There are no non-member users in this server")

            # Prints out a list of commands that users can execute
            elif command == "!help" or command == "!h":

                print("\n" + author.name + " requested help")

                outp = ""
                member = False
                core = False

                if len(content) == 0:
                    member = True

                else:
                    if content == "member" or content == "members":
                        member = True
                    if content == "core" or content == "lead" or content == "leadership" or content == "all":
                        core = True
                        member = True

                if core is False and member is False:
                    outp += "\"" + content + "\" is not a valid argument\n"

                if member:
                    outp += "**Member Commands:**\n"
                    outp += "- !help (level) - leave arg blank for a list of member commands or use \"core\" to list " \
                            "all commands\n"
                    outp += "- !join (role) - adds you to the given role. If arg \"all\" is given then " \
                            "it adds you to all available roles\n"
                    outp += "- !leave (role) - removes you from the given role\n"
                    outp += "- !listRoles - lists all joinable roles\n"
                    outp += "- !unjoinedRoles - lists all roles you have not joined\n"
                    outp += "- !myRoles - lists the roles you are currently in\n"

                if core:
                    outp += "\n**Core Commands:**\n"
                    outp += "- !addMembers (@name) (@name2) (...) - adds all the given users to members. Must be of " \
                            "Core role or higher to use\n"
                    outp += "- !getRoles (@name) - lists the roles the specified user is in\n"
                    outp += "- !testChannels - Tests all the channels on the server and pings the author if the bot " \
                            "can write messages in it. This shows what channels are vulnerable "

                outp += "\nIf you find any bugs please tell Chris Heidelberg (AiByte#6141) so he can fix it. Thanks!"

                await client.send_message(channel, outp)
            else:
                await client.send_message(channel, ("\"" + command + "\" is not a known command"))
                print("\n" + author.name + " used unknown command \"" + command + "\"")

        else:
            print("\na non-member \"" + author.name + "\" tried to use a bot command")
            await client.send_message(channel, "You must be a member before you can use the bot")

        # -------------------------------------------------------------------------------------------------------------


# Code to run before the discord bot goes online

# Give the location of the file
local = os.path.dirname(os.path.realpath(__file__))
delCsv = (local + "/DeletedMessages.csv")
logCsv = (local + "/LoggedMessages.csv")

# Reads token and server id from txt file
try:
    file = open(local + '/token.txt', 'r')
    info = file.readlines()
except FileNotFoundError:
    print("Cant find file \"" + local + "/token.txt\"")
    print("Either it doesnt exist or this program doesnt have permission to access it")
    sys.exit(1)

# Checks to make sure the txt file is populated
if len(info) == 2:
    TOKEN = info[0].rstrip()
    serverID = info[1].rstrip()
else:
    print("token.txt must have two lines. First line for token second line for serverID")
    print("Most likely issue token.txt does not have text in it.")
    sys.exit(0)

# Checks if token is valid and boots bot
try:
    client.run(TOKEN)
except discord.errors.LoginFailure:
    print("Invalid bot token in token.txt")
    sys.exit(0)
except SystemExit:
    print("Program forced itself closed")
