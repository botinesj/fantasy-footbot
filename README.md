**THIS PROJECT IS A WORK IN PROGRESS**

This is a Discord Bot I created. It performs a variety of actions related to Fantasy Football. The features it currently provides are:

* View Top Ranked Players
  * Displays the top ranked players based on the scoring format. 
User's have the option of viewing rankings by position or overall. Positional 
rankings display the top 5 players at every position. Overall rankings display 
the top X players overall, where X is given by the user. The user can indicate 
whether their league contains IDP's and the positional rankings will account for this. 
Overall rankings do not not support IDP leagues.

* View A Specific Player's Stats
  * Displays various statistics for a specific given player.

* Who Should I Start?
  * Given two players (including DST's) and a scoring format, displays 
the percentage of fantasy football experts that recommend starting one player over 
the other for the current game week. DST's can only be compared with other DST'S. 
The same applies to K's.

* My Team
  * Display's players on your team. You may add and remove players as 
you desire. This bot will remember these players for you.

I have plans to implement more Fantasy Football actions as well as general actions related to the NFL, such as:
* Watchlist - A watchlist of players not on your team
* View NFL Schedule
* What team should I bet on?

<h2>Video Demonstration</h3> 
https://streamable.com/wnp28j

<h2>How to run</h3> 
<h4>Requirements</h4>
You must have downloaded MySql and BeautifulSoup.

<h4>Steps</h4> 
1. Copy this repo. Then you will need to create a new Discord bot and invite it to the desired server. These steps are outlined here: https://discordpy.readthedocs.io/en/latest/discord.html  
  
*db.py*  
3. Replace PASSWORD in db.py with the password for your MySql account   
4. Uncomment the code from lines 14-18  
5. Run db.py  
6. Comment the code from lines 14-18  
7. Remove line 2: "from config import PASSWORD" 
  
*bot.py*  
8. Replace TOKEN in line 551 with the the token of the new bot you created in step 1  
9. Run bot.py  

 
