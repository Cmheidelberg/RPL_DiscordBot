import discord
from discord.ext import commands
import csv
import os
import sys


#Global variables
client = commands.Bot(command_prefix = '!')
membersRole = None;
coreRole = None;

#Searches through an array of roles for the role with the matching name
def findRoleIndex(content,roleList):
    for i in range(len(roleList)):
        currRole = roleList[i]

        if(content.lower() == currRole.name.lower()):
            return i

    return -1;

#checks if the user has the role "member"
def hasMember(author):
    global membersRole;
    for i in range(len(author.roles)):
        if(author.roles[i] == membersRole):
            return True;

    return False;

#Checks if the given author has coreRole
def hasCore(author):
    global coreRole;
    
    for i in range(len(author.roles)):
        if(author.roles[i].position >= coreRole.position):
            return True;

    return False;

#Tries to add the author to the given role
@client.event
async def addRole(author,channel,content):
    
    serverRoles = author.server.roles;
    index = findRoleIndex(content,serverRoles);

    #Checks to see if role exists
    if(index > 0):
        currRole = serverRoles[index];

        #This section checks to see if the author is already in the requested role
        if(-1 == findRoleIndex(currRole.name,author.roles)):

            try:
                await client.add_roles(author, currRole);
                await client.send_message(channel,"You joined " + currRole.name);
                print(author.name + " joined the role");

            except:
                await client.send_message(channel,currRole.name + " is locked and cannot be joined");
                print(author.name + " tried to join a restricted role (bot permissions too low)");

        else:
           print(author.name + " was already in that role");
           await client.send_message(channel,"You are already in of that role");
                
    else:
        await client.send_message(channel,"That role does not exist");
        print("Role does not exist");
  
#detects when bot is ready
@client.event
async def on_ready():
    global membersRole,serverID,coreRole;
    try:
        serverRoles = client.get_server(serverID).roles;
    except:
        print("Invalid serverID in token.txt file");

    #Finds members and core roles
    membersRole = findRoleIndex("members",serverRoles);
    coreRole = findRoleIndex("core",serverRoles);

    if membersRole != -1:
        membersRole = serverRoles[membersRole];
        coreRole = serverRoles[coreRole];
        print('Members and Core roles configured')
    else:
        print("Failed to configured members role!")
        sys.exit(0);

    if(len(client.get_server(serverID).me.roles) > 2):
        print("Bot should only be in one role (The bot role)");
        sys.exit(0);
        
    #Checks to see if the bot has a role of Bot
    if(findRoleIndex("bot",client.get_server(serverID).me.roles) != -1):
        print("Bot is in propor role")
    else:
        print("Bot needs to be in role \"Bot\"")
        sys.exit(0);
            
    
    print('Bot is online and active')

#does something when someone deletes a message
##@client.event
##async def on_message_delete(message):
##    print('Logged Deleted message by: {}'.format(message.author));
##    time = message.timestamp;
##    
##    #The 'a' means it will append to the end of the csv
##    with open(delCsv, 'a', newline='') as csvfile:
##        deleteLogger = csv.writer(csvfile, delimiter=',',quotechar='|', quoting=csv.QUOTE_MINIMAL)
##        deleteLogger.writerow([message.author] + [message.content] + [message.channel] + [time.date()] + [time.time()]);

#Use on_message so the bot runs on every message sent. Also checks if certain commands were entered
@client.event
async def on_message(message):
    global membersRole,coreRole;
    wholeString = message.content.split()
    command = wholeString[0];
    command = command.lower();

    #gets discord objects so the bot can use them as needed
    author = message.author;
    channel = message.channel;
    server = message.server;
    
    if(command[0] == '!'):
        
        if(hasMember(author)):

            #Gets the users "message" (ignores command prefex ie: "!join")
            del wholeString[0];
            content = ' '.join(wholeString);
            content[1:]
            content = content.lower();
    
            #User commands below
            #---------------------------------------------------------------------------------------- 

            #Tries to give the author user the specified role
            if(command == "!join"):
                print("\nAttempting to give " + author.name + " a role: " + content);

                #checks if user gave an argument
                if(len(content) > 0):

                    #Assigns user all available roles
                    if(content == "all"):
                        serverRoles = channel.server.roles;
                        
                        for i in range(len(serverRoles)):
                            botRoleIndex = findRoleIndex("bot",message.server.me.roles)

                            currRole = serverRoles[i];
                            if((i > 0 and currRole.position < message.server.me.roles[botRoleIndex].position) and (currRole != membersRole)):
                                await client.add_roles(author, currRole);

                        print("gave " + author.name + " all available roles");
                        await client.send_message(channel,"You have been added to all available roles");
                                
                    else:
                        await addRole(author,channel,content);
                                                  
                else:
                    await client.send_message(channel,"Must provide at least one argument");
                    print(author.name + " used join without arguments");

            #Tries to remove the author from a specified role
            elif(command == "!leave"):
                print("\n" + author.name + " wants to leave a role: " + content);

                if(len(content) > 0):
                    authorRoles = author.roles;
                    mem = membersRole.name
                    
                    if(content != mem):
                        index = findRoleIndex(content, authorRoles);
                        if(index > 0):
                            try:
                                await client.remove_roles(author,authorRoles[index]);
                                await client.send_message(channel,"You are no longer in " + authorRoles[index].name);
                                print(author.name + " left " + authorRoles[index].name);
                            except:
                                print("Bot does not have permission to remove role")
                                await client.send_message(channel,"I cannot remove you from this role")
                        else:
                            await client.send_message(channel,"You have no role \"" + content + "\" maybe you misspelled it?");
                            print(author.name + " is not in that role")
                    else:
                        print("User tried to leave members role")
                        await client.send_message(channel,"Cannot leave members role. If you want to leave member role ask a team leader or admin to remove you");
                    
                else:
                    print("user did not provide argument")
                    await client.send_message(channel,"Must provide at least one argument")
            #lists roles joinable by all members
            elif(command == "!listroles"):
                print("\n" + author.name + " requested a list of roles")
                serverRoles = channel.server.roles;
                outp = "**Server Roles:**\n";
                
                for i in range(len(serverRoles)):
                    botRoleIndex = findRoleIndex("bot",message.server.me.roles)
                    currRole = serverRoles[i];
                    if( (i > 0 and currRole.position < message.server.me.roles[botRoleIndex].position) and (currRole != membersRole)):
                            outp += "\t" + currRole.name + "\n";                            

                await client.send_message(channel,outp);

            elif(command == "!listunjoined" or command == "!listunjoinedroles" or command == "!listjoinable"
                 or command == "!listjoinableroles" or command == "!unjoinedroles"):
                print("\n" + author.name + " requested a list of unjoined roles")
                serverRoles = channel.server.roles;
                outp = "**Unjoined Roles:**\n";
                    
                for i in range(len(serverRoles)):
                    botRoleIndex = findRoleIndex("bot",message.server.me.roles)
                    currRole = serverRoles[i];
                    if( (i > 0 and findRoleIndex(currRole.name,author.roles) == -1 and currRole.position < message.server.me.roles[botRoleIndex].position) and (currRole != membersRole)):
                            outp += "\t" + currRole.name + "\n";                            
                if(len(outp) > 20):
                    await client.send_message(channel,outp);
                else:
                    await client.send_message(channel,"You are already in all joinable roles");

            #Lists the roles of a user
            elif(command == "!myroles" or command == "!getroles" or command == "!getrole" or command == "!myrole"):
                print("\n" + author.name + " requested the roles of a user")

                userRoles = None;
                name = None;
                outp = "";

                #If a name is given to check
                if(len(content) > 0):

                     if(len(message.mentions) > 0):
                         name = message.mentions[0].name;
                         userRoles = message.mentions[0].roles;
                     else:
                        #loops through all members in the server to find input name
                        for i in range(len(server.members)):

                            currMember = list(server.members);
                            currMember = currMember[i];

                            
                            if(content == currMember.name.lower() or content == currMember.display_name.lower() or content == currMember.id.lower()):
                                name = currMember.name;
                                userRoles = currMember.roles;
                                break;
        
                #in no input is given     
                else:
                    userRoles = author.roles;
                    name = author.name

                #if user is found 
                if(name != None and userRoles != None):        
                    outp += "**" + name + "\'s Roles:**\n";

                    for i in range(len(userRoles)):
                        if(i > 0):
                            outp += "\t" + str(i) + ". " + userRoles[i].name + "\n";

                    await client.send_message(channel,outp);
                    print("Showing roles for " + name)

                #If the name is not in the server
                else:
                    print(author.name + " did not provide a valid argument");
                    await client.send_message(channel,"Cannot find that user. check spelling");
                    

                
            #adds all mentioned (@name) users to the members role
            elif(command == "!addmembers" or command == "!addmember"):
                print("\n" + author.name + " is trying to add a new member")                
                outp = '';
                
                #if the author has permission to issue this command    
                if(hasCore(author)):

                    addedNewMember = False;
                    for i in range(len(message.mentions)):
                         
                        currPerson = message.mentions[i];
                        #if the user isnt already in the members role
                        if(False == hasMember(currPerson)):
                            print("new member " + currPerson.name + " added")
                            await client.add_roles(currPerson, membersRole);
                            addedNewMember = True;
                            outp += "Welcome " + currPerson.mention + " to the USCRPL server " + '\n';
                        else:
                            print(currPerson.name + " is already in the members role");

                    if(addedNewMember == True):
                        outp += "When you are ready use !listRoles for a list of the joinable roles. Then use !join (role) to view the different text channels";
                else:
                    print(author.name + " doesnt have permission to add member")
                    outp = "You dont have permission to add member";

                #sends all updates as one message to prevent delay
                await client.send_message(channel,outp); 

            #Tries to message in all text channels. If the bot can message in a channel it isnt supposed to then that channel is vunerable
            elif(command == "!tc" or command == "!testchannels"):

                print("\n" + author.name + " is testing channel security");
                if(hasCore(author)):
                    
                    allSecure = True;
                    count = 0;
                    channels = list(server.channels);

                    await client.send_message(channel,"Testing all text channels for vunerability, this will take a few moments");

                    #This can actually be made more efficient by checking permissions before trying to send a message (sending a message has lag)
                    for i in range(len(channels)):
                        if(channels[i].type == discord.ChannelType.text and channels[i] != channel):
                            try:
                                await client.send_message(channels[i],author.mention);
                                print(channels[i].name + " can be accessed and messaged by bot")
                                allSecure = False;
                            except:
                                count += 1;

                    if(allSecure):
                        print("All channels secure");
                        await client.send_message(channel,"Done");
                    else:
                        await client.send_message(channel,"Done. You have been pinged in all channels the bot can access");
                            
                else:
                    print(author.name + " doesnt have permission to test channels")
                    await client.send_message(channel,"You need to be a core member to use this command");

            #Prints out a list of commands that users can excecute
            elif(command == "!help" or command == "!h"):

                print("\n" + author.name + " requested help");

                outp = "";
                member = False;
                core = False;

                if(len(content) == 0):
                    member = True;
                    
                else:
                    if(content == "member" or content == "members"):
                        member = True;
                    if(content == "core" or content == "lead" or content == "leadership" or content == "all"):
                        core = True;
                        member = True;

                if(core == False and member== False):
                    outp += "\"" + content + "\" is not a valid argument\n";
                    
                if(member):
                    outp += "**Member Commands:**\n"
                    outp += "- !help (level) - leave arg blank for a list of member commands or use \"core\" to list all commands\n";
                    outp += "- !join (role) - adds you to the given role. If arg \"all\" is given then it adds you to all available roles\n";
                    outp += "- !leave (role) - removes you from the given role\n";
                    outp += "- !listRoles - lists all joinable roles\n";
                    outp += "- !unjoinedRoles - lists all roles you have not joined\n";
                    outp += "- !myRoles - lists the roles you are currently in\n";


                if(core):
                    outp += "\n**Core Commands:**\n" 
                    outp += "- !addMembers (@name) (@name2) (...) - adds all the given users to members. Must be of Core role or higher to use\n";
                    outp += "- !getRoles (@name) - lists the roles the specified user is in\n"
                    outp += "- !testChannels - Tests all the channels on the server and pings the author if the bot can write messages in it. This shows what channels are vunerable"
                    
                outp += "\nIf you find any bugs please tell Chris Heidelberg (AiByte#6141) so he can fix it. Thanks!"

                await client.send_message(channel,outp);
            else:
                await client.send_message(channel,("\"" + command + "\" is not a known command"));
                print("\n" + author.name + " used unknown command \"" + command + "\"");
        
        else:
            print("\na non-member \"" + author.name + "\" tried to use a bot command")
            await client.send_message(channel,"You must be a member before you can use the bot");

        #-------------------------------------------------------------------------------------------------------------
#Code to run before the discord bot goes online

# Give the location of the file
local = os.path.dirname(os.path.realpath(__file__));
delCsv = (local + "/DeletedMessages.csv")
logCsv = (local + "/LoggedMessages.csv") 

#Reads token and server id from txt file
try:
    file = open(local + '/token.txt', 'r') 
    info = file.readlines();
except:
    print("Cant find file \"" + local + "/token.txt\"")
    print("Either it doesnt exist or this program doesnt have permission to access it")
    sys.exit(0);

#Checks to make sure the txt file is populated
if(len(info) == 2):
    TOKEN = info[0].rstrip();
    serverID = info[1].rstrip();
else:
    print("token.txt must have two lines. First line for token second line for serverID")
    print("Most likely issue token.txt does not have text in it.")
    sys.exit(0);

#Checks if token is valid and boots bot
try:
    client.run(TOKEN);
except:
    print("\nSomething went wrong in the discord client, if an error is above this message than that is the problem otherwise there is an invalid token in or network" + local + "/token.txt. Or your internet went down")
    sys.exit(0);    
