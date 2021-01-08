import discord
from discord.ext import commands
import requests
import bs4
from bs4 import BeautifulSoup
import mysql.connector as mysql
import db
from db import mycursor, mydb

client = commands.Bot(command_prefix='.')


def scoring_format_check(msg):
    return msg.content.upper() in ["STANDARD", "PPR", "HALF"]


def position_check(msg):
    return msg.content.upper() in ["QB", "RB", "WR", "TE", "K", "DST", "DL", "LB", "DB"]


def yes_no_check(msg):
    return msg.content.lower() in ["yes", "no"]


def ovr_pos_check(msg):
    return msg.content.lower() in ["overall", "position"]


def myteam_check(msg):
    return msg.content.upper() in ["ADD", "REMOVE"]


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('/options'):
        await message.channel.send('Here are the options:\n'
                                   '.top - View Top Ranked Players\n'
                                   ".specific - View A Specific Player's Stats\n"
                                   ".who - Who Should I Start?\n"
                                   ".watch - Watch List\n"
                                   ".myteam - My Team\n"
                                   "To be added later - View NFL Schedule\n"
                                   "To be added later - Who Should I bet on?\n")
    await client.process_commands(message)


@client.command()
async def top(ctx):
    await ctx.send("Does your league contain IDP's? Please enter 'Yes' or 'No'")
    yn_response = await client.wait_for('message', check=yes_no_check)
    answer1 = yn_response.content.upper()

    await ctx.send("What is the Scoring format? Please enter one of the following:\n"
                   "Standard\n"
                   "PPR\n"
                   "Half\n")
    scoring_response1 = await client.wait_for('message', check=scoring_format_check)
    scoring_format1 = scoring_response1.content.upper()

    await ctx.send("Do you want to see overall rankings or by position? Please enter one of the following:\n"
                   "Overall (Does not contain IDP's for now)\n"
                   "Position\n")
    rankings_response = await client.wait_for('message', check=ovr_pos_check)
    answer2 = rankings_response.content.upper()

    if answer2 == "OVERALL":
        if scoring_format1 == "STANDARD":
            r = requests.get('https://www.fantasypros.com/nfl/reports/leaders/?year=2020')
            soup = bs4.BeautifulSoup(r.text, features="html.parser")
        elif scoring_format1 == "HALF":
            r = requests.get('https://www.fantasypros.com/nfl/reports/leaders/half-ppr.php?year=2020')
            soup = bs4.BeautifulSoup(r.text, features="html.parser")
        elif scoring_format1 == "PPR":
            r = requests.get('https://www.fantasypros.com/nfl/reports/leaders/ppr.php?year=2020')
            soup = bs4.BeautifulSoup(r.text, features="html.parser")
        for tr in soup.find_all('tr')[1:51]:
            tds = tr.find_all('td')
            await ctx.send("Rank: " + tds[0].text + ", Player: " + tds[1].text + ", Team: " + tds[2].text + ", Points: " + tds[3].text +
                           ", Games: " + tds[4].text + ", AVG: " + tds[5].text)
    else:
        positions = ["QB", "RB", "WR", "TE", "K", "DST", "DL", "LB", "DB"]

        if answer1 == "YES":
            new_positions = positions[:5] + positions[6:]
        else:
            new_positions = positions[:6]
        for pos in new_positions:
            if pos in ["QB", "K", "DST", "DL", "LB", "DB"] or scoring_format1 == "STANDARD":
                r = requests.get('https://www.fantasypros.com/nfl/reports/leaders/' + pos.lower() + '.php?year=2020')
                soup = bs4.BeautifulSoup(r.text, features="html.parser")
            elif scoring_format1 == "HALF":
                r = requests.get('https://www.fantasypros.com/nfl/reports/leaders/half-ppr-'+ pos.lower() +'.php?year=2020')
                soup = bs4.BeautifulSoup(r.text, features="html.parser")
            elif scoring_format1 == "PPR":
                r = requests.get('https://www.fantasypros.com/nfl/reports/leaders/ppr-'+ pos.lower() +'.php?year=2020')
                soup = bs4.BeautifulSoup(r.text, features="html.parser")
            await ctx.send('======================='+pos+'=======================')
            for tr in soup.find_all('tr')[1:6]:
                if pos == "DST":
                    tds = tr.find_all('td')
                    await ctx.send("Rank: " + tds[0].text + ", Team: " + tds[1].text + ", Points: " + tds[2].text + ", Games: " + tds[3].text +
                                   ", AVG: " + tds[4].text)
                else:
                    tds = tr.find_all('td')
                    await ctx.send("Rank: " + tds[0].text + ", Player: " + tds[1].text + ", Team: " + tds[2].text + ", Points: " + tds[3].text +
                                   ", Games: " + tds[4].text + ", AVG: " + tds[5].text)

@client.command()
async def specific(ctx):
    await ctx.send("What is the player's position? Please enter one of the following:\n"
                   "QB\n"
                   "RB\n"
                   "WR\n"
                   "TE\n"
                   "K\n"
                   "DST\n")
    position_response = await client.wait_for('message', check=position_check)
    position = position_response.content.upper()
    scoring_format2 = "STANDARD"
    if position not in ["QB", "DST"]:
        await ctx.send("What is the Scoring format? Please enter one of the following:\n"
                       "Standard\n"
                       "PPR\n"
                       "Half\n")
        scoring_response2 = await client.wait_for('message', check=scoring_format_check)
        scoring_format2 = scoring_response2.content.upper()

    await ctx.send("What is the player's full name? (You must omit numbers and suffixes from a player's name. For example, Patrick Mahomes II -> Patrick Mahomes and Michael Pittman Jr. -> Michael Pittman)")
    name_response = await client.wait_for('message')
    player_name = name_response.content.lower()

    if scoring_format2 == "STANDARD":
        r = requests.get('https://www.fantasypros.com/nfl/reports/leaders/?year=2020')
        soup = bs4.BeautifulSoup(r.text, features="html.parser")
    elif scoring_format2 == "HALF":
        r = requests.get('https://www.fantasypros.com/nfl/reports/leaders/half-ppr.php?year=2020')
        soup = bs4.BeautifulSoup(r.text, features="html.parser")
    elif scoring_format2 == "PPR":
        r = requests.get('https://www.fantasypros.com/nfl/reports/leaders/ppr.php?year=2020')
        soup = bs4.BeautifulSoup(r.text, features="html.parser")

    is_displayed = False
    for tr in soup.find_all('tr')[1:]:
        tds = tr.find_all('td')
        # print(tds[1].text.lower()) Need to get rid of
        com_player_name = tds[1].text.lower()
        if " iii" in com_player_name:
            com_player_name = com_player_name.replace(" iii", "")
        elif " ii" in com_player_name:
            com_player_name = com_player_name.replace(" ii", "")
        elif " jr." in com_player_name:
            com_player_name = com_player_name.replace(" jr.", "")
        if com_player_name == player_name and position.upper() == tds[3].text:
            await ctx.send("Overall Rank: " + tds[0].text + ", Player: " + tds[1].text + ", Team: " + tds[2].text + ", Position: " + tds[3].text +
                           ", Points: " + tds[4].text + ", Games: " + tds[5].text + ", AVG: " + tds[6].text)
            is_displayed = True
    if not is_displayed:
        await ctx.send("No player exists with that name and position. Please "
                       "make sure that the full name of the player is typed in "
                       "correctly and the corresponding position is correct.")

@client.command()
async def who(ctx):
    # DST not working yet
    await ctx.send("Note: You can only compare a DST with another DST. Otherwise, this bot will not work.")
    await ctx.send("What is the Scoring format? Please enter one of the following:\n"
                   "Standard\n"
                   "PPR\n"
                   "Half\n")
    scoring_response3 = await client.wait_for('message', check=scoring_format_check)
    scoring_format3 = scoring_response3.content.upper()

    await ctx.send("What is the first player's position? Please enter one of the following:\n"
                   "QB\n"
                   "RB\n"
                   "WR\n"
                   "TE\n"
                   "K\n"
                   "DST\n")
    p1_pos_response = await client.wait_for('message', check=position_check)
    position1 = p1_pos_response.content.upper()

    await ctx.send("What is the first player's full name? (You must omit numbers and suffixes from a player's name. For example, Patrick Mahomes II -> Patrick Mahomes and Michael Pittman Jr. -> Michael Pittman)")
    name_response = await client.wait_for('message')
    player_name1 = name_response.content.lower()

    if scoring_format3 == "STANDARD":
        r = requests.get('https://www.fantasypros.com/nfl/reports/leaders/?year=2020')
        soup = bs4.BeautifulSoup(r.text, features="html.parser")
    elif scoring_format3 == "HALF":
        r = requests.get('https://www.fantasypros.com/nfl/reports/leaders/half-ppr.php?year=2020')
        soup = bs4.BeautifulSoup(r.text, features="html.parser")
    elif scoring_format3 == "PPR":
        r = requests.get('https://www.fantasypros.com/nfl/reports/leaders/ppr.php?year=2020')
        soup = bs4.BeautifulSoup(r.text, features="html.parser")

    is_displayed = False
    p1_name = None
    for tr in soup.find_all('tr')[1:]:
        tds = tr.find_all('td')
        # print(tds[1].text.lower()) Need to get rid of
        com_player_name = tds[1].text.lower()
        if " iii" in com_player_name:
            com_player_name = com_player_name.replace(" iii", "")
        elif " ii" in com_player_name:
            com_player_name = com_player_name.replace(" ii", "")
        elif " jr." in com_player_name:
            com_player_name = com_player_name.replace(" jr.", "")
        if com_player_name == player_name1 and position1.upper() == tds[3].text:
            await ctx.send("VALID PLAYER")
            await ctx.send("Overall Rank: " + tds[0].text + ", Player: " + tds[1].text + ", Team: " + tds[2].text + ", Position: " + tds[3].text +
                           ", Points: " + tds[4].text + ", Games: " + tds[5].text + ", AVG: " + tds[6].text)
            is_displayed = True
            p1_name = com_player_name
    if not is_displayed:
        await ctx.send("No player exists with that name and position. Please "
                       "restart the command and make sure that the full name of "
                       "the player is typed in correctly and the corresponding "
                       "position is correct.")
    # THIS PART STILL SHOWS UP EVEN IF PREVIOUS PART IS ERROR. I WOULD ADD A VARIABLE TO CHECK. Indent all code below for if check and change a variable
    await ctx.send("What is the second player's position? Please enter one of the following:\n"
                   "QB\n"
                   "RB\n"
                   "WR\n"
                   "TE\n"
                   "K\n"
                   "DST\n")
    p2_pos_response = await client.wait_for('message', check=position_check)
    position2 = p2_pos_response.content.upper()

    await ctx.send("What is the second player's full name? (You must omit numbers and suffixes from a player's name. For example, Patrick Mahomes II -> Patrick Mahomes and Michael Pittman Jr. -> Michael Pittman)")
    name_response = await client.wait_for('message')
    player2_name = name_response.content.lower()

    is_displayed2 = False
    p2_name = None
    for tr in soup.find_all('tr')[1:]:
        tds = tr.find_all('td')
        # print(tds[1].text.lower()) Need to get rid of
        com_player2_name = tds[1].text.lower()
        if " iii" in com_player2_name:
            com_player2_name = com_player2_name.replace(" iii", "")
        elif " ii" in com_player2_name:
            com_player2_name = com_player2_name.replace(" ii", "")
        elif " jr." in com_player2_name:
            com_player2_name = com_player2_name.replace(" jr.", "")
        if com_player2_name == player2_name and position2.upper() == tds[3].text:
            await ctx.send("VALID PLAYER")
            await ctx.send("Overall Rank: " + tds[0].text + ", Player: " + tds[1].text + ", Team: " + tds[2].text + ", Position: " + tds[3].text +
                           ", Points: " + tds[4].text + ", Games: " + tds[5].text + ", AVG: " + tds[6].text)
            is_displayed2 = True
            p2_name = com_player2_name
    if not is_displayed2:
        await ctx.send("No player exists with that name and position. Please "
                       "restart the command and make sure that the full name of "
                       "the player is typed in correctly and the corresponding "
                       "position is correct.")

    # Player Name Exceptions (There is more than 1 player with that name)
    if p1_name == "michael thomas":
        p1_name = "michael thomas wr"
    if p2_name == "michael thomas":
        p2_name = "michael thomas wr"


    cities =["arizona", "baltimore", "buffalo", "carolina", "chicago", "cleveland", "dallas", "denver", "detroit", "green bay",
             "houston", "indianapolis", "jacksonville", "kansas city", "los angeles", "miami", "minnesota", "new england",
             "new orleans", "philadelphia", "pittsburgh", "san francisco", "seattle", "tennessee", "washington"]

    if is_displayed and is_displayed2:
        # if position1 and position2 == "DST":
        # LAC  - > san diego defense
        # NYG and NYJ need full names

        p1_name = p1_name.replace(" ", "-")
        p2_name = p2_name.replace(" ", "-")
        # if position1 and position2 == "DST":
        #     position1_hyphen_count = position1.count("-")
        #     position2_hyphen_count = position2.count("-")
        #     if position1_hyphen_count == 1: # MAKE INTO FUNCTION!!!
        #         "-".join(position1.split("-", 1)[:1])
        #     else:
        #         "-".join(position1.split("-", 2)[:2])
        #     if position2_hyphen_count == 1:
        #         "-".join(position2.split("-", 1)[:1])
        #     else:
        #         "-".join(position2.split("-", 2)[:2])





        if scoring_format3 == "STANDARD":
            r = requests.get('https://www.fantasypros.com/nfl/start/' + p1_name + "-" + p2_name + '.php')
            soup2 = bs4.BeautifulSoup(r.text, features="html.parser")
        elif scoring_format3 == "HALF":
            r = requests.get('https://www.fantasypros.com/nfl/start/' + p1_name + "-" + p2_name + '.php?scoring=HALF')
            soup2 = bs4.BeautifulSoup(r.text, features="html.parser")
        elif scoring_format3 == "PPR":
            r = requests.get('https://www.fantasypros.com/nfl/start/' + p1_name + "-" + p2_name + '.php?scoring=PPR')
            soup2 = bs4.BeautifulSoup(r.text, features="html.parser")

        await ctx.send("The results are in:")
        loop_counter = 0
        for tr in soup2.find_all('tr')[1:3]:
            tds = tr.find_all('td')
            if loop_counter == 0:
                hpyhen1 = tds[1].text.find("-")
                name1_print = tds[1].text[:hpyhen1 + 5]
                hpyhen2 = tds[2].text.find("-")
                name2_print = tds[2].text[:hpyhen2 + 5]
                await ctx.send("Player 1: " + name1_print + " vs Player 2: " + name2_print)
            else:
                # Formatting
                percentage1 = tds[1].text.find("%")
                percentage2 = tds[2].text.find("%")
                by1 = tds[1].text.find("by")
                by2 = tds[2].text.find("by")
                result1_print = tds[1].text[:percentage1 + 1] + " " + tds[1].text[percentage1 + 1: by1 + 2] + " " + tds[1].text[by1 + 2:]
                result2_print = tds[2].text[:percentage2 + 1] + " " + tds[2].text[percentage2 + 1: by2 + 2] + " " + tds[2].text[by2 + 2:]
                await ctx.send(result1_print + " --- " + result2_print)
            loop_counter += 1


@client.command()
async def myteam(ctx):
    # display current team members
    # ask if user wants to add a new member or drop a member
    # If empty, display specific message
    user_id = ctx.author.id
    # if discord_id is not in USER table, add it
    query = "SELECT userID FROM Users"
    mycursor.execute(query)
    records = mycursor.fetchall()
    id_exists = False
    for record in records:
        if user_id == record[0]:
            id_exists = True
    if not id_exists:
        await ctx.send("Please enter a team name:")
        name_response = await client.wait_for('message')
        team_name = name_response.content
        query = "INSERT INTO Users (userID, team_name) VALUES (%s, %s)"
        values = (user_id, team_name)
        mycursor.execute(query, values)
        mydb.commit()
    # Display Team Name
    query1 = "SELECT team_name FROM Users WHERE userID = " + str(user_id)
    mycursor.execute(query1)
    records1 = mycursor.fetchall() # fetchone gives records var above for some reason
    await ctx.send("============" + records1[0][0].upper() + "============")

    # CODE TAKEN FROM SPECIFIC - I AM REPEAING THEREFORE SHOULD PROB MAKE INTO FUNCTION OR SOMETHING
    await ctx.send("What would you like to do? Please enter one of the following:\n"
                   "ADD - Add a player to your team\n"
                   "REMOVE - Remove a player from your team\n")
    action_response = await client.wait_for('message', check=myteam_check)
    action = action_response.content.upper()

    if action == "ADD":
        await ctx.send("What is the player's position? Please enter one of the following:\n"
                       "QB\n"
                       "RB\n"
                       "WR\n"
                       "TE\n"
                       "K\n"
                       "DST\n")

    # CODE TAKEN FROM SPECIFIC - I AM REPEAING THEREFORE SHOULD PROB MAKE INTO FUNCTION OR SOMETHING
    position_response = await client.wait_for('message', check=position_check)
    position = position_response.content.upper()
    scoring_format2 = "STANDARD"
    if position not in ["QB", "DST"]:
        await ctx.send("What is the Scoring format? Please enter one of the following:\n"
                       "Standard\n"
                       "PPR\n"
                       "Half\n")
        scoring_response2 = await client.wait_for('message', check=scoring_format_check)
        scoring_format2 = scoring_response2.content.upper()

    await ctx.send("What is the player's full name? (You must omit numbers and suffixes from a player's name. For example, Patrick Mahomes II -> Patrick Mahomes and Michael Pittman Jr. -> Michael Pittman)")
    name_response = await client.wait_for('message')
    player_name = name_response.content.lower()

    if scoring_format2 == "STANDARD":
        r = requests.get('https://www.fantasypros.com/nfl/reports/leaders/?year=2020')
        soup = bs4.BeautifulSoup(r.text, features="html.parser")
    elif scoring_format2 == "HALF":
        r = requests.get('https://www.fantasypros.com/nfl/reports/leaders/half-ppr.php?year=2020')
        soup = bs4.BeautifulSoup(r.text, features="html.parser")
    elif scoring_format2 == "PPR":
        r = requests.get('https://www.fantasypros.com/nfl/reports/leaders/ppr.php?year=2020')
        soup = bs4.BeautifulSoup(r.text, features="html.parser")

    is_displayed = False
    for tr in soup.find_all('tr')[1:]:
        tds = tr.find_all('td')
        # print(tds[1].text.lower()) Need to get rid of
        com_player_name = tds[1].text.lower()
        if " iii" in com_player_name:
            com_player_name = com_player_name.replace(" iii", "")
        elif " ii" in com_player_name:
            com_player_name = com_player_name.replace(" ii", "")
        elif " jr." in com_player_name:
            com_player_name = com_player_name.replace(" jr.", "")
        if com_player_name == player_name and position.upper() == tds[3].text:
            await ctx.send("Overall Rank: " + tds[0].text + ", Player: " + tds[1].text + ", Team: " + tds[2].text + ", Position: " + tds[3].text +
                           ", Points: " + tds[4].text + ", Games: " + tds[5].text + ", AVG: " + tds[6].text)
            is_displayed = True
    if not is_displayed:
        await ctx.send("No player exists with that name and position. Please "
                       "make sure that the full name of the player is typed in "
                       "correctly and the corresponding position is correct.")


    # await ctx.send("Does your league contain IDP's? Please enter 'Yes' or 'No'")
    # await ctx.send("Does your league contain IDP's? Please enter 'Yes' or 'No'")
    # yn_response = await client.wait_for('message', check=yes_no_check)
    # answer1 = yn_response.content.upper()
    #     # add player - verify its a realy player then save it
    #     # delete player - verify that player is real, verify that player is on the team, then delete










if __name__ == '__main__':
    import config
    client.run(config.TOKEN)



# To fix: .who and .specific sometimes it counts its own messages as input which is an issue
# .who - New Orleans for michael thomas and any player really as NOM
# Need to fix Defense .who
