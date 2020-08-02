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

def add_game_logging():
    """
    Adds Custom gamestep loglevel and attaches logfunction to logging facility
    """
    logging.addLevelName(15, "GAMESTEP")
    logging.Logger.gamestep = gamestep


class Base_game:

    # Name of the game first team is the home team
    name = None

    # start conditions
    teams = {}
    snitch = None
    weather = 0

    # team indices
    start_i = None
    last_i = None
    next_chaser = [0,0]
    next_beater = [0,0]

    # results
    game_results = {}
    game_turns = 0
    score = [0,0]
    ending_team = None

    def __init__(self, name, team_file=None):
        """
            Initiates Base Game quidditch class

            Parameter
            ----------
            name : str
                Name of the Game
            team_file : str
                Path and name of team file
        """
        self.name = name
        self.weather = 0
        add_game_logging()
        if team_file:
            self.load_teams(team_file)

    def load_teams(self, filename):
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
                self.teams = json.load(lfile)
        return teams



    def dice_roll(self, stats=0):
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


    def beater_action(self, beaters, active=0):
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
        roll = self.dice_roll(stats["base"] + stats["mod"] + stats["temp"] + self.weather) 
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


    def chaser_action(self, chasers, active):
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
        roll = self.dice_roll(stats["base"] + stats["mod"] + stats["temp"] + self.weather) 
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


    def keeper_action(self, keeper):
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
        roll = self.dice_roll(keeper["base"] + keeper["mod"] + keeper["temp"] + self.weather) 
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


    def seeker_action(self, seeker):
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
        roll = self.dice_roll(stats["base"] + stats["mod"] + stats["streak"] + stats["temp"] + self.weather) 
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


    def pre_game(self, use_weather):
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
                start_i : int
                    index of starting team
                last_i : int
                    index of second team
        """
        if use_weather:
            conditions = self.dice_roll()
            if conditions <= 6:
                self.weather = -2
                gamelogger.gamestep("Really bad weather conditions")
            elif conditions <= 9:
                self.weather -= 1
                gamelogger.gamestep("Bad weather conditions")
            else:
                gamelogger.gamestep("Good weather conditions")
        # decide witch team starts the match
        team1 = 0
        team2 = 0
        while team1 == team2:
            team1 = self.dice_roll()
            team2 = self.dice_roll()
        if team1 > team2:
            self.start_i = 0
            gamelogger.gamestep("the Home Team {} Starts\n".format(self.teams[0]["Name"]))
        else:
            self.start_i = 1
            gamelogger.gamestep("the Guest Team {} Starts\n".format(self.teams[1]["Name"]))
        # calculate index of second team
        self.last_i = (self.start_i + 1) % 2
        return {
            "weather": self.weather,
            "start_i": self.start_i,
            "last_i": self.last_i
        }


    def run_game(self, use_duplicate_roles=True, use_weather=False):
        """
            Performs quidditch player actions until the snitch is cought

            Parameters
            ----------
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
                start_i : String
                    Name of Team starting the match
                weather : int
                    Weather modifyer for the game
        """
        # set up game variables
        self.snitch = False

        # Pre game loop rolls
        self.pre_game(use_weather)

        # temporary results
        action_results = {}

        # fetch team indices for quick acces
        start_i = self.start_i
        last_i = self.last_i

        # fetch team Names for quick access
        team_1_name = self.teams[start_i]["Name"]
        team_2_name = self.teams[last_i]["Name"]
        
        # run game simulation
        while not self.snitch:
            self.game_turns += 1
            # Chaser Actions
            # first team Chaser
            gamelogger.gamestep("{} Chaser".format(team_1_name))
            action_results = self.chaser_action(self.teams[start_i]["Chaser"], self.next_chaser[start_i])
            self.score[start_i] += action_results ["own"]
            self.score[last_i] += action_results["other"]
            if use_duplicate_roles:
                self.next_chaser[start_i] = (self.next_chaser[start_i] + 1) % len(self.teams[start_i]["Chaser"])
            # second team Chaser
            gamelogger.gamestep("{} Chaser".format(team_2_name))
            action_results = self.chaser_action(self.teams[last_i]["Chaser"], self.next_chaser[last_i])
            self.score[last_i] += action_results["own"]
            self.score[start_i] += action_results["other"]
            if use_duplicate_roles:
                self.next_chaser[last_i] = (self.next_chaser[last_i] + 1) % len(self.teams[last_i]["Chaser"])
            # Beater Actions
            # first team Beater
            gamelogger.gamestep("{} Beater".format(team_1_name))
            action_results = self.beater_action(self.teams[start_i]["Beater"], self.next_beater[start_i])
            self.score[start_i] += action_results["own"]
            self.score[last_i] += action_results["other"]
            if use_duplicate_roles:
                self.next_beater[start_i] = (self.next_beater[start_i] + 1) % len(self.teams[start_i]["Beater"])
            # second team Beater
            gamelogger.gamestep("{} Beater".format(team_2_name))
            action_results = self.beater_action(self.teams[last_i]["Beater"],self.next_beater[last_i])
            self.score[last_i] += action_results["own"]
            self.score[start_i] += action_results["other"]
            if use_duplicate_roles:
                self.next_beater[last_i] = (self.next_beater[last_i] + 1) % len(self.teams[last_i]["Beater"])
            # Keeper Actions
            # first team Keeper
            gamelogger.gamestep("{} Keeper".format(team_1_name))
            action_results = self.keeper_action(self.teams[start_i]["Keeper"])
            self.score[start_i] += action_results["own"]
            self.score[last_i] += action_results["other"]
            # second team Keeper
            gamelogger.gamestep("{} Keeper".format(team_2_name))
            action_results = self.keeper_action(self.teams[last_i]["Keeper"])
            self.score[last_i] += action_results["own"]
            self.score[start_i] += action_results["other"]
            # Seeker Actions
            # first team Seeker
            gamelogger.gamestep("{} Seeker".format(team_1_name))
            action_results = self.seeker_action(self.teams[start_i]["Seeker"])
            if action_results["snitch"]:
                # check if snitch was cought
                self.snitch = True
                self.score[start_i] += 150
                self.ending_team = self.teams[start_i]["Name"]
                break            
            elif action_results["streak"] < 0:
                self.teams[start_i]["Seeker"]["temp"] -= action_results["streak"]
                self.teams[start_i]["Seeker"]["streak"] = 0
            else: 
                self.teams[start_i]["Seeker"]["streak"] = action_results["streak"]
            # second team Seeker
            gamelogger.gamestep("{} Seeker".format(team_2_name))
            action_results = self.seeker_action(self.teams[last_i]["Seeker"])
            if action_results["snitch"]:
                self.snitch = True
                self.score[last_i] += 150
                self.ending_team = self.teams[last_i]["Name"]
                break
            elif action_results["streak"] < 0:
                self.teams[last_i]["Seeker"]["temp"] -= action_results["streak"]
                self.teams[last_i]["Seeker"]["streak"] = 0
            else:
                self.teams[last_i]["Seeker"]["streak"] = action_results["streak"]
            # ensure no team is below 0 points
            self.score = [max(i,0) for i in self.score]
            # end of round logs
            gamelogger.gamestep("\nRound {} Score Summary".format(self.game_turns))
            gamelogger.gamestep("{}: {} - {}: {}\n".format(self.teams[0]["Name"], self.score[0], self.teams[1]["Name"], self.score[1]))
            logger.info("Turn {} Score: {} - {}".format(self.game_turns, self.score[0], self.score[1]))
        # Post Game 
        scores = {
            self.teams[0]["Name"]: self.score[0],
            self.teams[1]["Name"]: self.score[1]
        }
        self.game_results= {
            "ending_team": self.ending_team,
            "game_turns": self.game_turns,
            "score": scores,
            "start_team": self.teams[start_i]["Name"],
            "weather": self.weather
        }
        # send basic info to logger
        logger.info("Match Finished after {} turns".format(self.game_turns))
        logger.info("{} ended the Match".format(self.ending_team))
        # send in depth info to game logger
        gamelogger.gamestep("\n{} ended the Game!".format(self.ending_team))
        gamelogger.gamestep("Final Score:")
        gamelogger.gamestep("{} {} - {} {}".format(
            self.teams[0]["Name"], self.score[0],
            self.teams[1]["Name"], self.score[1]
        ))
        self.score = scores
        return self.game_results


if __name__ == "__main__":
    args = parser.parse_args()
    # load team file
    try:
        name = str(args.team_file).rsplit(sep='/', maxsplit=1)[-1].rsplit(sep='.',maxsplit=1)[0]
        game = Base_game(name)
        teams = game.load_teams(args.team_file)
        # setup logging parameter
        gamelogger = logging.getLogger("GameLogger")
        gamelogger.setLevel(15)        
        if args.collect_metadata:
            # setup log file handler
            gamehandler = logging.FileHandler("{}.txt".format(game.name))
            gamelogger.addHandler(gamehandler)
        # run game
        result = game.run_game(use_duplicate_roles=args.single_roles, use_weather=args.use_weather)
        # dump result into file
        with open("{}_result.json".format(game.name),mode="w") as result_file:
            json.dump(result, result_file, sort_keys=True, indent=4)
    except OSError as e:
        logger.error("unable to load file: \n" + e)
    except IndexError as e2:
        logger.error(e2)