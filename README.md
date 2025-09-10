# UBC A Cappella Sniped Bot v1.0!
Welcome to the Discord Sniped Bot designed for use in UBC A Cappella!  
This bot exists to facilitate gameplay by keeping track of scores, leaderboards, and acheivements.  
If you run into any issues or have ideas for additional features please message me on discord: @oriose

To add the bot to your server, click this link here: [**Invite Bot!**](https://discord.com/oauth2/authorize?client_id=1361870886885527572&permissions=275146476608&scope=applications.commands+bot)

## Features
*Commands marked by * can only be used by users with the `@Sniped Control` role*
### Game Start:  
`/help` Lists all available commands  
`/initgame`* Initializes game for the server, initial settings configuration are as such:  

    points_per_snipe: 1.0
    penalty_per_snipe: 1.0
    acheivements_enabled: True
    safe_times: None

`/config`* View or change the settings of your game \
`/safetime`* Add, remove, or view safetimes \
`/resetgame`* Reset all game data and settings for your server  
`/joingame` Add yourself to the game \
`/addplayer`* Add a player to the game  
`/removeplayer`* Remove a player and all snipes related to them

### Gameplay:
`/snipe` Snipe a player! \
`/deletesnipe`* Remove an invalid snipe 

### Leaderboard:
`/leaderboard` Show the current points leaderboard  
`/listplayers` List all players in the game \
`/listsnipes` List a number of recent snipes

### 



## How To Play
This section explains the rules of sniped as NWC plays, your group may alter the rules to suit your own preferences.

### Goal:
Take pictures of other players without them knowing and try to avoid getting pictures taken of you!

### Sniping:
- All snipes must occur without the target knowing
  - Pictures must be snapped and sent to the correct channel before the target sees the sniper  
  - The target can deny the point if they have some proof that they knew  
  - This is heavily based on the honour system

- The snipe does not need to include the target's face, but the target must be recognizable
- If two or more players are together and send a snipe of the same target(s), only the first snipe sent will count
  - If two or more players are not together but happen to snipe the same target in the same location, they can all get the points
- A snipe including multiple players together counts as +1 point for each target in the shot
- +3 Points if you snipe someone while they are sniping someone else (snipeception -- not implemented yet)

### Safe Zones:
- All Aca events are safe times
  - This includes rehearsals, sectionals, concerts, and hangouts
  - Players not involved in these events can still snipe/be sniped
  - Sniping cannot occur for players involved for 15 minutes before/after the event
- Shared Classes are safe times
  - Players not in these classes can still snipe/be sniped
  - Sniping cannot occur for members involved for 10 minutes before/after the class
- Snipes cannot occur in the UBC A Cappella Clubroom
  - This does not include the communcal clubs area just outside of the clubroom


## Version Changelog
### V1.1
- Snipe confirmation message now resends every 2h

### V1.0
- Game is ready to play!
- Currently hosted on gcloud VM
- Updates to come with additional features!


### V0.4
- Added confirmation message when sniped
- Implemented safetime checks

### V0.3
- Added control role: marked commands now require role to use
- Added safety checks for init
- Safetimes can now be added to config (they are not in use yet)


### V0.2
- Added removeplayer
- Added deletesnipe
- Fixed resetgame
- /config now shows current configuration when no arguments passed
- Removals now require confirmation


### V0.1
- Converted all data storage from JSON to MongoDB



