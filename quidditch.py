import logging
import argparse
import json
import random

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# argument parser
parser = argparse.ArgumentParser(description="Run a game of quidditch,")
parser.add_argument('--team-file', required=True, type=str, help="File location and name containing a 2 element list of team collections")
parser.add_argument("--single-roles", action="store_false", help="set only use 1 player per roll of the teams.")
parser.add_argument("--use-weather", action="store_true", help="set to include Weather modifyer for the game")
parser.add_argument("--collect-metadata", action="store_true", help="set collect Game Metadata")

def __init__():
    logging.addLevelName(15, "GAMESTEP")
    logging.Logger.gamestep = gamestep


def load_teams(filename):
    """
    Loads a Match json file containing two teams
    
    Parameters
    ----------
    filename : str
        Filepath and name to location
    
    Returns
    ----------
    List
        List of two Team data objects
    """
    teams = {}
    with open(filename,mode="r") as lfile:
            teams = json.load(lfile)
    return teams


def gamestep(self, message, *args, **kws):
    """
    enables logging for gamestep level
    
    Parameters
    ----------
    self
    message: string
        Message sent at log level
    *args
    **kws
    """
    if self.isEnabledFor(15):
        self._log(15, message, args, **kws) 


def dice_roll(stats=0):
    """
        Rolls two six sided dice and adds optional modifyer

        Parameters
        ----------
        stats : int
            Summary of all bonuses and penalties to applied to the roll
        
        Returns
        ----------
        int
            Returns Result of the roll
    """
    roll = random.randint(1,6) + random.randint(1,6) + stats
    return roll


def beater_action(beaters, active=0, weather=0):
    """
        Performs a standard beater action

        Parameters
        ----------
        beaters : list
            List of Beater modifyer collection (dict)
            Dict Parameter:
            base : int
                relevant Player attribute for the role
            mod : int
                long term non weather modifyer (Conditions)
            temp : int
                one time use modifyer
        active : int
            Index of Beater taking the turn. leave empty when you only use one beater 
        weather : int
            Weather modifyer for the game. leave empty if not applied for the game     
        
        Returns
        ----------
        dict
            collection of relative game point chances.

            Dict Parameter:
            own : int
                changes to own teams points
            other : int
                changes to other teams points
    """
    # chooses the modifyer of the active player alternating between beaters
    stats = beaters[active]
    # roll with player stats + long term modifyers and one time temporary ones and weather if applied
    roll = dice_roll(stats["base"] + stats["mod"] + stats["temp"] + weather) 
    # relative score changes
    game = {"own": 0, "other": 0}
    if roll >= 10:
        # on success
        game["own"] += 10
        game["other"] -= 10
        gamelogger.gamestep("{}: Success ".format(beaters[active].get("Name", "Beater" + str(active))))
    elif roll >= 7:
        # on partial success
        game["own"] += 10
        gamelogger.gamestep("{}: Partial Success".format(beaters[active].get("Name", "Beater" + str(active))))
    else:
        # on fail
        game["other"]  += 10
        gamelogger.gamestep("{}: Fail ".format(beaters[active].get("Name", "Beater" + str(active))))
    return game


def chaser_action(chasers, active, weather=0):
    """
        Performs a standard Chaser action

        Parameters:
        ----------
        chasers : list
            List of Chaser modifyer collection (dict)
            Dict Parameter:
            base : int
                relevant Player attribute for the role
            mod : int
                long term non weather modifyer (Conditions)
            temp : int
                one time use modifyer
        active : int
            Index of Chaser taking the turn. leave empty when you only use one beater
        weather : int
            Weather modifyer for the game. leave empty if not applied for the game     
        
        Returns
        ----------
        dict
            collection of relative game point chances.

            Dict Parameter:
            own : int
                changes to own teams points
            other : int
                changes to other teams points
    """
    # choose modifyer of active player
    stats = chasers[active]
    # roll with player stats + long term modifyers and one time temporary ones and weather if applied
    roll = dice_roll(stats["base"] + stats["mod"] + stats["temp"] + weather) 
    # relative score changes
    game = {"own": 0, "other": 0}
    if roll >= 10:
        # on success
        game["own"] +=20
        gamelogger.gamestep("{}: Success".format(chasers[active].get("Name", "Chaser" + str(active))))
    elif roll >= 7:
        # on partial success
        game["own"] += 10
        gamelogger.gamestep("{}: Partial Success".format(chasers[active].get("Name", "Chaser" + str(active))))
    else:
        # on fail
        game["other"] += 10
        gamelogger.gamestep("{}: Fail".format(chasers[active].get("Name", "Chaser" + str(active))))
    return game


def keeper_action(keeper, weather=0):
    """
        Performs a standard Keeper action

        Parameters
        ----------
        keeper : dict
            Keeper modifyer collection
            Dict Parameter:
            base : int
                relevant Player attribute for the role
            mod : int
                long term non weather modifyer (Conditions)
            temp : int
                one time use modifyer
        weather : int
            Weather modifyer for the game. leave empty if not applied for the game     
        
        Returns
        ----------
        dict
            collection of relative game point chances.
            Dict Parameter:
            own : int
                changes to own teams points
            other : int
                changes to other teams points
    """
   # roll with player stats + long term modifyers and one time temporary ones and weather if applied
    roll = dice_roll(keeper["base"] + keeper["mod"] + keeper["temp"] + weather) 
    # relative score changes
    game = {"own": 0, "other": 0}
    if roll >= 10:
        game["own"] += 10
        game["other"] -= 10
        gamelogger.gamestep("{}: Success".format(keeper.get("Name","Keeper")))
    elif roll >= 7:
        game["other"] -= 10
        gamelogger.gamestep("{}: Partial Success".format(keeper.get("Name","Keeper")))
    else:
        game["other"] += 10
        gamelogger.gamestep("{}: Fail".format(keeper.get("Name","Keeper")))
    return game


def seeker_action(seeker, weather=0):
    """
        Performs a standard Seeker action

        Parameters
        ----------
        Seeker : dict
            Seeker modifyer collection
            Dict Parameter:
            base : int
                relevant Player attribute for the role
            mod : int
                long term non weather modifyer (Conditions)
            streak : int
                Sum of all previous (partial) success modifyer
            temp : int
                one time use modifyer
        weather : int
            Weather modifyer for the game. leave empty if not applied for the game     
        
        Returns
        ----------
        dict
            collection of resulting Seeker state.
            Dict Parameter:
            streak : int
                new sum of success modifyer. returns -2 on a failed roll to apply to temporary modifyer
            snitch : boolean
                Flag if the snitch is cought to end the game
    """
    # get modifyer for seeker
    stats = seeker
    # roll with player stats + long term modifyers and one time temporary ones and weather if applied
    roll = dice_roll(stats["base"] + stats["mod"] + stats["streak"] + stats["temp"] + weather) 
    # seeker modifyer tracker
    game = {"streak": stats["streak"], "snitch": False}
    if roll >= 15:
        game["snitch"] = True
        gamelogger.gamestep("{} cought the Snitch!".format(seeker.get("Name","Seeker")))
    elif roll >= 10:
        game["streak"] += 2
        gamelogger.gamestep("{}: Success".format(seeker.get("Name","Seeker")))
        gamelogger.gamestep("current streak bonus {}".format(game["streak"]))
    elif roll >= 7:
        game["streak"] += 1
        gamelogger.gamestep("{}: Partial Success".format(seeker.get("Name","Seeker")))
        gamelogger.gamestep("current streak bonus {}".format(game["streak"]))
    else:
        game["streak"] = -1
        gamelogger.gamestep("{}: Fail".format(seeker.get("Name","Seeker")))
    return game


def pre_game(use_weather):
    """
        Handles Pre game loop calculations for weather and start team
        
        Parameters
        ----------
        use_weather : boolean
            Flag if weather should affect the game

        Returns
        ----------
        Dict
            Game parameter collection:
            Dict Parameter:
            weather : int
                weather modifyer applying to the game
            start_team : int
                index of starting team
            last_team : int
                index of second team
    """
    weather = 0
    if use_weather:
        conditions = dice_roll()
        if conditions <= 6:
            weather = -2
            gamelogger.gamestep("Really bad weather conditions")
        elif conditions <= 9:
            weather -= 1
            gamelogger.gamestep("Bad weather conditions")
        else:
            gamelogger.gamestep("Good weather conditions")
    # decide witch team starts the match
    team1 = 0
    team2 = 0
    while team1 == team2:
        team1 = dice_roll()
        team2 = dice_roll()
    if team1 > team2:
        start_team = 0
        gamelogger.gamestep("the Home Team Starts\n")
    else:
        start_team = 1
        gamelogger.gamestep("the Guest Team Starts\n")
    # calculate index of second team
    last_team = (start_team + 1) % 2
    return {
        "weather": weather,
        "start_team": start_team,
        "last_team": last_team
    }


def run_game(teams, use_duplicate_roles=True, use_weather=False):
    """
        Performs quidditch player actions until the snitch is cought

        Parameters
        ----------
        teams : List
            List of two team collections containing 2 Beater, 3 Chaser, Keeper
            and Seeker player collections
        use_duplicate_roles : boolean
            Flag if all beaters and chaser of a team should rolled with individual
            modifyers.
            Default: True
        use_weather : boolean
            Flag if weather modifyer should aplly to the game.
            Default: False

        Returns
        ----------
        Dict
            Collection of finished game statistics
            Dict Parameter:
            ending_team : String
                Name of Team catching the snitch
            game_turns : int
                number of full rounds the game went on
            score : dict
                team_1 : int
                team_2 : int
            start_team : String
                Name of Team starting the match
            weather : int
                Weather modifyer for the game
    """
    # when needed create log file
    # set up game variables
    snitch = False
    weather = 0
    action_results = {}
    # flag for beater and chaser for next action
    next_chaser = [0,0]
    next_beater = [0,0]
    # Pre game loop rolls
    start_cond = pre_game(use_weather)
    # result collection
    game_results = {
        "ending_team" : None,
        "game_turns": 0,
        "score" : [0,0],
        "start_team": teams[start_cond["start_team"]]["Name"],
        "weather": start_cond["weather"]
    }
    start_team = start_cond["start_team"]
    last_team = start_cond["last_team"]
    team_1_name = teams[start_team]["Name"]
    team_2_name = teams[last_team]["Name"]
    # run game simulation
    while not snitch:
        game_results["game_turns"] += 1
        # Chaser Actions
        # first team Chaser
        gamelogger.gamestep("{} Chaser".format(team_1_name))
        action_results = chaser_action(teams[start_team]["Chaser"],next_chaser[start_team],weather=weather)
        game_results["score"][start_team] += action_results["own"]
        game_results["score"][last_team] += action_results["other"]
        if use_duplicate_roles:
            next_chaser[start_team] = (next_chaser[start_team] + 1) % len(teams[start_team]["Chaser"])
        # second team Chaser
        gamelogger.gamestep("{} Chaser".format(team_2_name))
        action_results = chaser_action(teams[last_team]["Chaser"],next_chaser[last_team],weather=weather)
        game_results["score"][last_team] += action_results["own"]
        game_results["score"][start_team] += action_results["other"]
        if use_duplicate_roles:
            next_chaser[last_team] = (next_chaser[last_team] + 1) % len(teams[last_team]["Chaser"])
        # Beater Actions
        # first team Beater
        gamelogger.gamestep("{} Beater".format(team_1_name))
        action_results = beater_action(teams[start_team]["Beater"], next_beater[start_team],weather=weather)
        game_results["score"][start_team] += action_results["own"]
        game_results["score"][last_team] += action_results["other"]
        if use_duplicate_roles:
            next_beater[start_team] = (next_beater[start_team] + 1) % len(teams[start_team]["Beater"])
        # second team Beater
        gamelogger.gamestep("{} Beater".format(team_2_name))
        action_results = beater_action(teams[last_team]["Beater"],next_beater[last_team],weather=weather)
        game_results["score"][last_team] += action_results["own"]
        game_results["score"][start_team] += action_results["other"]
        if use_duplicate_roles:
            next_beater[last_team] = (next_beater[last_team] + 1) % len(teams[last_team]["Beater"])
        # Keeper Actions
        # first team Keeper
        gamelogger.gamestep("{} Keeper".format(team_1_name))
        action_results = keeper_action(teams[start_team]["Keeper"],weather=weather)
        game_results["score"][start_team] += action_results["own"]
        game_results["score"][last_team] += action_results["other"]
        # second team Keeper
        gamelogger.gamestep("{} Keeper".format(team_2_name))
        action_results = keeper_action(teams[last_team]["Keeper"],weather=weather)
        game_results["score"][last_team] += action_results["own"]
        game_results["score"][start_team] += action_results["other"]
        # Seeker Actions
        # first team Seeker
        gamelogger.gamestep("{} Seeker".format(team_1_name))
        action_results = seeker_action(teams[start_team]["Seeker"], weather=weather)
        if action_results["snitch"]:
            # check if snitch was cought
            snitch = True
            game_results["score"][start_team] += 150
            game_results["ending_team"] = teams[start_team]["Name"]
            break            
        elif action_results["streak"] < 0:
            teams[start_team]["Seeker"]["temp"] -= 2
            teams[start_team]["Seeker"]["streak"] = 0
        else: 
            teams[start_team]["Seeker"]["streak"] = action_results["streak"]
        # second team Seeker
        gamelogger.gamestep("{} Seeker".format(team_2_name))
        action_results = seeker_action(teams[last_team]["Seeker"], weather=weather)
        if action_results["snitch"]:
            snitch = True
            game_results["score"][last_team] += 150
            game_results["ending_team"] = teams[last_team]["Name"]
            break
        elif action_results["streak"] < 0:
            teams[last_team]["Seeker"]["temp"] -= 2
            teams[last_team]["Seeker"]["streak"] = 0
        else:
             teams[last_team]["Seeker"]["streak"] = action_results["streak"]
        # ensure no team is below 0 points
        game_results["score"] = [max(i,0) for i in game_results["score"]]
        # end of round logs
        gamelogger.gamestep("\nRound {} Score Summary".format(game_results["game_turns"]))
        gamelogger.gamestep("{}: {} - {}: {}\n".format(teams[0]["Name"], game_results["score"][0], teams[1]["Name"], game_results["score"][1]))
        logger.info("Turn {} Score: {} - {}".format(game_results["game_turns"], game_results["score"][0], game_results["score"][1]))
    # Post Game 
    # send basic info to logger
    logger.info("Match Finished after {} turns".format(game_results["game_turns"]))
    logger.info("{} ended the Match".format(game_results["ending_team"]))
    # send in depth info to game logger
    gamelogger.gamestep("\n{} ended the Game!".format(game_results["ending_team"]))
    gamelogger.gamestep("Final Score:")
    gamelogger.gamestep("{} {} - {} {}".format(
        teams[0]["Name"], game_results["score"][0],
        teams[1]["Name"], game_results["score"][1]
    ))
    #increase score verbosity
    scores = {
        teams[start_team]["Name"]: game_results["score"][start_team],
        teams[last_team]["Name"]: game_results["score"][last_team]
    }
    game_results["score"] = scores
    return game_results


if __name__ == "__main__":
    args = parser.parse_args()
    # load team file
    try:
        teams = load_teams(args.team_file)
        # setup logging parameter
        __init__()
        gamelogger = logging.getLogger("GameLogger")
        gamelogger.setLevel(15)        
        if args.collect_metadata:
            # setup log file handler
            gamehandler = logging.FileHandler("{}_vs_{}.txt".format(teams[0]["Name"], teams[1]["Name"]))
            gamelogger.addHandler(gamehandler)
        # run game
        result = run_game(teams,use_duplicate_roles=args.single_roles,use_weather=args.use_weather)
        # dump result into file
        with open("{}_vs_{}_result.json".format(teams[0]["Name"], teams[1]["Name"]),mode="w") as result_file:
            json.dump(result, result_file, sort_keys=True, indent=4)
    except OSError as e:
        logger.error("unable to load file: \n" + e)
    except IndexError as e2:
        logger.error(e2)