from discord.ext import commands
import requests
import bs4
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


def not_bot_check(msg):
    return msg.author != client.user


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
        await message.channel.send("Here are the options:\n"
                                   "• .top - View Top Ranked Players\n"
                                   "Description - Displays the top ranked "
                                   "players based on the scoring format. "
                                   "User's have the option of viewing rankings "
                                   "by position or overall. Positional rankings"
                                   " display the top 5 players at every "
                                   "position. Overall rankings display the top"
                                   " 50 players overall. The user can "
                                   "indicate whether their league contains "
                                   "IDP's and the positional rankings will account "
                                   "for this. Overall rankings do not not "
                                   "support IDP leagues.\n"
                                   "• .specific - View A Specific Player's Stats\n"
                                   "Description - Displays various statistics "
                                   "for a specific given player.\n"
                                   "• .who - Who Should I Start?\n"
                                   "Description - Given two players (including "
                                   "DST's) and a scoring format, displays the "
                                   "percentage of fantasy football experts that "
                                   "recommend starting one player over the "
                                   "other for the current game week. DST's can "
                                   "only be compared with other DST'S. The "
                                   "same applies to K's.\n"
                                   "• .myteam - My Team\n"
                                   "Description - Display's players on your "
                                   "team. You may add and remove players as you"
                                   " desire. This bot will remember these "
                                   "players for you.\n"
                                   "• To be added later - Watch List\n"
                                   "• To be added later - View NFL Schedule\n"
                                   "• To be added later - Who Should I bet on?\n")
    await client.process_commands(message)


@client.command()
async def top(ctx):
    await ctx.send("Does your league contain IDP's? Please enter 'Yes' or 'No':")
    yn_response = await client.wait_for('message', check=yes_no_check)
    answer1 = yn_response.content.upper()

    await ctx.send("What is the Scoring format? Please enter one of the following:\n"
                   "• Standard\n"
                   "• PPR\n"
                   "• Half\n")
    scoring_response1 = await client.wait_for('message', check=scoring_format_check)
    scoring_format1 = scoring_response1.content.upper()

    await ctx.send("Do you want to see overall rankings or by position? Please enter one of the following:\n"
                   "• Overall (Does not contain IDP's)\n"
                   "• Position\n")
    rankings_response = await client.wait_for('message', check=ovr_pos_check)
    answer2 = rankings_response.content.upper()

    soup = None
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
            await ctx.send("Rank: " + tds[0].text + ", Player: " + tds[1].text + ", Team: " + tds[2].text + ", Position: " + tds[3].text +
                           ", Points: " + tds[4].text + ", Games: " + tds[5].text+ ", AVG per game: " + tds[6].text)
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
                   "• QB\n"
                   "• RB\n"
                   "• WR\n"
                   "• TE\n"
                   "• K\n"
                   "• DST\n")
    position_response = await client.wait_for('message', check=position_check)
    position = position_response.content.upper()
    scoring_format2 = "STANDARD"
    if position not in ["QB", "DST"]:
        await ctx.send("What is the Scoring format? Please enter one of the following:\n"
                       "• Standard\n"
                       "• PPR\n"
                       "• Half\n")
        scoring_response2 = await client.wait_for('message', check=scoring_format_check)
        scoring_format2 = scoring_response2.content.upper()

    await ctx.send("What is the player's full name? (You must omit numbers and suffixes from a player's name. For example, Patrick Mahomes II -> Patrick Mahomes and Michael Pittman Jr. -> Michael Pittman. If it is a DST, please enter the team's full name. For example, Washington Football Team)")
    name_response = await client.wait_for('message', check=not_bot_check)
    player_name = name_response.content.lower()

    soup = None
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
        await ctx.send("No player exists with that name and position. You'll "
                       "have to start the command again. Please "
                       "make sure that the full name of the player is typed in "
                       "correctly and the corresponding position is correct.")


@client.command()
async def who(ctx):
    await ctx.send("Note: You can only compare a DST with another DST and a K "
                   "with another K. Otherwise, this bot will not work.")
    await ctx.send("What is the Scoring format? Please enter one of the following:\n"
                   "• Standard\n"
                   "• PPR\n"
                   "• Half\n")
    scoring_response3 = await client.wait_for('message', check=scoring_format_check)
    scoring_format3 = scoring_response3.content.upper()

    await ctx.send("What is the first player's position? Please enter one of the following:\n"
                   "• QB\n"
                   "• RB\n"
                   "• WR\n"
                   "• TE\n"
                   "• K\n"
                   "• DST\n")
    p1_pos_response = await client.wait_for('message', check=position_check)
    position1 = p1_pos_response.content.upper()

    await ctx.send("What is the first player's full name? (You must omit numbers and suffixes from a player's name. For example, Patrick Mahomes II -> Patrick Mahomes and Michael Pittman Jr. -> Michael Pittman"
                   "If it is a DST, please enter the team's full name. For example, Washington Football Team)")
    name_response = await client.wait_for('message', check=not_bot_check)
    player_name1 = name_response.content.lower()
    soup = None
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
        return
    await ctx.send("What is the second player's position? Please enter one of the following:\n"
                   "• QB\n"
                   "• RB\n"
                   "• WR\n"
                   "• TE\n"
                   "• K\n"
                   "• DST\n")
    p2_pos_response = await client.wait_for('message', check=position_check)
    position2 = p2_pos_response.content.upper()

    await ctx.send("What is the second player's full name? (You must omit numbers and suffixes from a player's name. For example, Patrick Mahomes II -> Patrick Mahomes and Michael Pittman Jr. -> Michael Pittman)")
    name_response = await client.wait_for('message', check=not_bot_check)
    player2_name = name_response.content.lower()

    is_displayed2 = False
    p2_name = None
    for tr in soup.find_all('tr')[1:]:
        tds = tr.find_all('td')
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
        return

    # Player Name Exceptions (There is more than 1 player with that name)
    if p1_name == "michael thomas":
        p1_name = "michael thomas wr"
    if p2_name == "michael thomas":
        p2_name = "michael thomas wr"


    cities =["arizona", "baltimore", "buffalo", "carolina", "chicago", "cleveland", "dallas", "denver", "detroit", "green bay",
             "houston", "indianapolis", "jacksonville", "kansas city", "los angeles", "miami", "minnesota", "new england",
             "new orleans", "philadelphia", "pittsburgh", "san francisco", "seattle", "tampa bay", "tennessee", "washington"]

    if is_displayed and is_displayed2:
        if position1 and position2 == "DST":
            if p1_name == "los angeles chargers":
                p1_name = "san diego"
            if p2_name == "los angeles chargers":
                p2_name = "san diego"
            if p1_name != "new york giants" or "new york jets": # NYG and NYJ need full names
                for city in cities:
                    if city in p1_name:
                        start_ind = p1_name.find(city)
                        p1_name = p1_name[start_ind:len(city)]
            if p2_name != "new york giants" or "new york jets": # NYG and NYJ need full names
                for city in cities:
                    if city in p2_name:
                        start_ind = p2_name.find(city)
                        p2_name = p2_name[start_ind:len(city)]
            p1_name += " defense"
            p2_name += " defense"

        p1_name = p1_name.replace(" ", "-")
        p2_name = p2_name.replace(" ", "-")
        soup2 = None
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
    user_id = ctx.author.id
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
    records1 = mycursor.fetchall() # fetchone gives records variable above for some reason
    await ctx.send("============" + records1[0][0].upper() + "============")

    query3 = "SELECT position, name, team FROM User_Roster WHERE userID = " + str(user_id)
    mycursor.execute(query3)
    records3 = mycursor.fetchall()
    for record in records3:
        await ctx.send(record[0] + "-" + record[1] + "-" + record[2])
    if records3 == []:
        await ctx.send("Your team has no players.")

    await ctx.send("What would you like to do? Please enter one of the following:\n"
                   "• ADD - Add a player to your team\n"
                   "• REMOVE - Remove a player from your team\n")
    action_response = await client.wait_for('message', check=myteam_check)
    action = action_response.content.upper()

    if action == "ADD":
        await ctx.send("What is the player's position? Please enter one of the following:\n"
                       "• QB\n"
                       "• RB\n"
                       "• WR\n"
                       "• TE\n"
                       "• K\n"
                       "• DST\n")

        position_response = await client.wait_for('message', check=position_check)
        position = position_response.content.upper()

        await ctx.send("What is the player's full name? (You must omit numbers and suffixes from a player's name. For example, Patrick Mahomes II -> Patrick Mahomes and Michael Pittman Jr. -> Michael Pittman)")
        name_response = await client.wait_for('message', check=not_bot_check)
        player_name = name_response.content.lower()

        # Making sure this is a valid Player
        r = requests.get('https://www.fantasypros.com/nfl/reports/leaders/?year=2020')
        soup = bs4.BeautifulSoup(r.text, features="html.parser")

        is_displayed = False
        p_add_name = None
        p_add_team = None
        p_add_position = None
        for tr in soup.find_all('tr')[1:]:
            tds = tr.find_all('td')
            com_player_name = tds[1].text.lower()
            if " iii" in com_player_name:
                com_player_name = com_player_name.replace(" iii", "")
            elif " ii" in com_player_name:
                com_player_name = com_player_name.replace(" ii", "")
            elif " jr." in com_player_name:
                com_player_name = com_player_name.replace(" jr.", "")
            if com_player_name == player_name and position.upper() == tds[3].text:
                await ctx.send("VALID PLAYER")
                p_add_name = tds[1].text
                p_add_team = tds[2].text
                p_add_position = tds[3].text
                is_displayed = True
        if not is_displayed:
            await ctx.send("No player exists with that name and position. Please "
                           "make sure that the full name of the player is typed in "
                           "correctly and the corresponding position is correct.")
            return

        # Check if player already on team
        query2 = "SELECT position, name, team FROM User_Roster WHERE userID = " + str(user_id)
        mycursor.execute(query2)
        records2 = mycursor.fetchall()
        player = (p_add_position, p_add_name, p_add_team)

        player_on_team = False
        for record in records2:
            if player == record:
                player_on_team = True

        if player_on_team:
            await ctx.send("Error. This player is already on your team.")
            return
        query = "INSERT INTO User_Roster (userID, position, name, team) VALUES (%s, %s, %s, %s)"
        values1 = (user_id, p_add_position, p_add_name, p_add_team)
        mycursor.execute(query, values1)
        mydb.commit()
        await ctx.send("Player added successfully.")
    else:
        await ctx.send("What is the player's position? Please enter one of the following:\n"
                       "• QB\n"
                       "• RB\n"
                       "• WR\n"
                       "• TE\n"
                       "• K\n"
                       "• DST\n")

        position_response = await client.wait_for('message', check=position_check)
        position = position_response.content.upper()

        await ctx.send("What is the player's full name? (You must omit numbers and suffixes from a player's name. For example, Patrick Mahomes II -> Patrick Mahomes and Michael Pittman Jr. -> Michael Pittman)")
        name_response = await client.wait_for('message', check=not_bot_check)
        player_name = name_response.content.lower()

        # Making sure this is a valid Player
        r = requests.get('https://www.fantasypros.com/nfl/reports/leaders/?year=2020')
        soup = bs4.BeautifulSoup(r.text, features="html.parser")

        is_displayed = False
        p_add_name = None
        p_add_team = None
        p_add_position = None
        for tr in soup.find_all('tr')[1:]:
            tds = tr.find_all('td')
            com_player_name = tds[1].text.lower()
            if " iii" in com_player_name:
                com_player_name = com_player_name.replace(" iii", "")
            elif " ii" in com_player_name:
                com_player_name = com_player_name.replace(" ii", "")
            elif " jr." in com_player_name:
                com_player_name = com_player_name.replace(" jr.", "")
            if com_player_name == player_name and position.upper() == tds[3].text:
                await ctx.send("VALID PLAYER")
                p_add_name = tds[1].text
                p_add_team = tds[2].text
                p_add_position = tds[3].text
                is_displayed = True
        if not is_displayed:
            await ctx.send("No player exists with that name and position. Please "
                           "make sure that the full name of the player is typed in "
                           "correctly and the corresponding position is correct.")
            return

        # Check if player on team
        query2 = "SELECT position, name, team FROM User_Roster WHERE userID = " + str(user_id)
        mycursor.execute(query2)
        records2 = mycursor.fetchall()
        player = (p_add_position, p_add_name, p_add_team)

        player_on_team = False
        for record in records2:
            if player == record:
                player_on_team = True

        if not player_on_team:
            await ctx.send("Error. This player is not on your team.")
            return

        # THIS FORMAT WILL NOT WORK
        # query4 = "DELETE FROM User_Roster WHERE userID = " + str(user_id) + \
        #          " AND position = " + p_add_position + \
        #          " AND name = " + p_add_name + " AND team = " + p_add_team

        query4 = "DELETE FROM User_Roster WHERE userID = %s and position = %s " \
                 "and name = %s and team = %s"
        values = (str(user_id), p_add_position, p_add_name, p_add_team)
        mycursor.execute(query4, values)
        mydb.commit()
        await ctx.send("Player deleted successfully.")

if __name__ == '__main__':
    import config
    client.run(config.TOKEN)

# To fix: .who and .specific sometimes it counts its own messages as input which is an issue
# add display top by position. Give them a prompt for how many they want to print
# add timeouts

