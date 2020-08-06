import logging
import argparse
import json
import random

logger = logging.getLogger(__name__)
sh = logging.StreamHandler()
logger.addHandler(sh)
logger.setLevel(logging.INFO)

# argument parser
parser = argparse.ArgumentParser(description="Run a game of quidditch,")
parser.add_argument('--team-file', required=True, type=str, help="File location and name containing a 2 element list of team collections")
parser.add_argument("--single-roles", action="store_true", help="set only use 1 player per roll of the teams.")
parser.add_argument("--use-weather", action="store_true", help="set to include Weather modifyer for the game")
parser.add_argument("--collect-metadata", action="store_true", help="set to collect Game Metadata")
parser.add_argument("--house-rules", action="store_true", help="set to use house rules")


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
            # Yes, logger takes its '*args' as 'args'.
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
    get_metadata = None
    use_weather = None
    single_roles = None
    # start conditions
    teams = {}
    snitch = None
    weather = 0

    # team indices
    start_i = None
    last_i = None
    team_1_name = ""
    team_2_name = ""
    next_chaser = [0,0]
    next_beater = [0,0]

    # results
    game_results = {}
    game_turns = 0
    score = [0,0]
    ending_team = None
    player_results = {}

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


    def add_track_record(self, name, status, team=None):
        """
            Adds and update player track records

            Parameters:
            ----------
            name : str
                Name of the player to track
            status : str
                Status of the player
        """
        tn = self.player_results.get(team,None)
        if not tn:
            self.player_results.update({team: {}})
        record = list(self.player_results[team].get(name,[]))
        record.append(status)
        self.player_results[team][name] = record


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


    def beater_action(self, beaters, active=0, team=None):
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
            Team : str
                Name of Team

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
        # get player name
        name = beaters[active].get("Name", "Beater" + str(active))
        # relative score changes
        game = {"own": 0, "other": 0}
        status = None
        if roll >= 10:
            # on success
            game["own"] += 10
            game["other"] -= 10
            gamelogger.gamestep("{}: Success ".format(name))
            status = 2
        elif roll >= 7:
            # on partial success
            game["own"] += 10
            gamelogger.gamestep("{}: Partial Success".format(name))
            status = 1
        else:
            # on fail
            game["other"]  += 10
            gamelogger.gamestep("{}: Fail ".format(name))
            status = 0
        if self.get_metadata:
            self.add_track_record(name,status, team)
        return game


    def chaser_action(self, chasers, active=0, team=None):
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
        # get player name
        name = chasers[active].get("Name", "Chaser" + str(active))
        # relative score changes
        game = {"own": 0, "other": 0}
        status = None
        if roll >= 10:
            # on success
            game["own"] +=20
            gamelogger.gamestep("{}: Success".format(chasers[active].get("Name", "Chaser" + str(active))))
            status = 2
        elif roll >= 7:
            # on partial success
            game["own"] += 10
            gamelogger.gamestep("{}: Partial Success".format(chasers[active].get("Name", "Chaser" + str(active))))
            status = 1
        else:
            # on fail
            game["other"] += 10
            gamelogger.gamestep("{}: Fail".format(chasers[active].get("Name", "Chaser" + str(active))))
            status = 0
        if self.get_metadata:
            self.add_track_record(name, status, team)
        return game


    def keeper_action(self, keeper, team=None):
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
        # get player name
        name = keeper.get("Name","Keeper")
        # relative score changes
        game = {"own": 0, "other": 0}
        status = None
        if roll >= 10:
            game["own"] += 10
            game["other"] -= 10
            gamelogger.gamestep("{}: Success".format(name))
            status = 2
        elif roll >= 7:
            game["other"] -= 10
            gamelogger.gamestep("{}: Partial Success".format(keeper.get("Name","Keeper")))
            status = 1
        else:
            game["other"] += 10
            gamelogger.gamestep("{}: Fail".format(keeper.get("Name","Keeper")))
            status = 0
        if self.get_metadata:
            self.add_track_record(name, status, team)
        return game


    def seeker_action(self, seeker, team=None):
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
        # get player name
        name = seeker.get("Name","Seeker")
        # roll with player stats + long term modifyers and one time temporary ones and weather if applied
        roll = self.dice_roll(stats["base"] + stats["mod"] + stats["streak"] + stats["temp"] + self.weather) 
        # seeker modifyer tracker
        game = {"streak": stats["streak"], "snitch": False}
        status = None
        if roll >= 15:
            game["snitch"] = True
            gamelogger.gamestep("{} cought the Snitch!".format(seeker.get("Name","Seeker")))
            status = 3
        elif roll >= 10:
            game["streak"] += 2
            gamelogger.gamestep("{}: Success".format(seeker.get("Name","Seeker")))
            gamelogger.gamestep("current streak bonus {}".format(game["streak"]))
            status = 2
        elif roll >= 7:
            game["streak"] += 1
            gamelogger.gamestep("{}: Partial Success".format(seeker.get("Name","Seeker")))
            gamelogger.gamestep("current streak bonus {}".format(game["streak"]))
            status = 1
        else:
            game["streak"] = -2
            gamelogger.gamestep("{}: Fail".format(name))
            status = 0
        if self.get_metadata:
            self.add_track_record(name, status, team)
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
        # fetch team Names for quick access
        self.team_1_name = self.teams[self.start_i]["Name"]
        self.team_2_name = self.teams[self.last_i]["Name"]
        return {
            "weather": self.weather,
            "start_i": self.start_i,
            "last_i": self.last_i
        }


    def chaser_turns(self, single_roles=False, use_all=False):
        """
            Performes all chaser actions for one turn

            Parameters
            ----------
            single_roles : boolean
                Flag if only one beater and chaser of a team should roll
                Default: False
            use_all : boolean
                Flag if all chasers are allowed to make a action (for house rules)
                Default: False

            Returns
            ----------
            list
                List with relative score changes ordered start team -> second team

        """
        score_change = [0,0]
        # when all player should be used invoke function recurively
        if use_all:
            for index in self.teams[self.start_i]["Chaser"]:
                changes = self.chaser_turns(single_roles=True)
                score_change[0] += changes[0]
                score_change[1] += changes[1]
                index = (index + 1) %len(self.teams[self.start_i]["chaser"])
        else:
            # temp result variables
            result_1 = {}
            result_2 = {}
            # first team Chaser
            gamelogger.gamestep("{} Chaser".format(self.team_1_name))
            result_1 = self.chaser_action(self.teams[self.start_i]["Chaser"], self.next_chaser[self.start_i], team=self.team_1_name)
            if not single_roles:
                self.next_chaser[self.start_i] = (self.next_chaser[self.start_i] + 1) % len(self.teams[self.start_i]["Chaser"])
            # second team Chaser
            gamelogger.gamestep("{} Chaser".format(self.team_2_name))
            result_2 = self.chaser_action(self.teams[self.last_i]["Chaser"], self.next_chaser[self.last_i], team=self.team_2_name) 
            if not single_roles:
                self.next_chaser[self.last_i] = (self.next_chaser[self.last_i] + 1) % len(self.teams[self.last_i]["Chaser"])
            score_change = [result_1["own"] + result_2["other"], result_1["other"] + result_2["own"]]
            self.score[self.start_i] += score_change[0]
            self.score[self.last_i	] += score_change[1]
            return [score_change]


    def beater_turns(self, single_roles=False, use_all=False):
        """
            Performes all Beater actions for one turn

            Parameters
            ----------
            single_roles : boolean
                Flag if only one beater and chaser of a team should roll
                Default: False
            use_all : boolean
                Flag if all chasers are allowed to make a action (for house rules)
                Default: False

            Returns
            ----------
            list
                List with relative score changes ordered start team -> second team
        """
        score_change = [0,0]
        # when all player should be used invoke function recurively
        if use_all:
            for index in self.teams[self.start_i]["Beater"]:
                changes = self.chaser_turns(single_roles=True)
                score_change[0] += changes[0]
                score_change[1] += changes[1]
                index = (index + 1) %len(self.teams[self.start_i]["Beater"])
        else:
            # temp result variables
            result_1 = {}
            result_2 = {}
            # first team Beater
            gamelogger.gamestep("{} Beater".format(self.team_1_name))
            result_1 = self.beater_action(self.teams[self.start_i]["Beater"], self.next_beater[self.start_i], team=self.team_1_name)
            if not single_roles:
                self.next_beater[self.start_i] = (self.next_beater[self.start_i] + 1) % len(self.teams[self.start_i]["Beater"])
            # second team Beater
            gamelogger.gamestep("{} Beater".format(self.team_2_name))
            result_2 = self.beater_action(self.teams[self.last_i]["Beater"], self.next_beater[self.last_i], team=self.team_2_name) 
            if not single_roles:
                self.next_beater[self.last_i] = (self.next_beater[self.last_i] + 1) % len(self.teams[self.last_i]["Beater"])
            score_change = [result_1["own"] + result_2["other"], result_1["other"] + result_2["own"]]
            self.score[self.start_i] += score_change[0]
            self.score[self.last_i	] += score_change[1]
            return[score_change]
            

    def keeper_turns(self):
        """
            Performes all Beater actions for one turn

            Parameters
            ----------
            single_roles : boolean
                Flag if only one beater and chaser of a team should roll
                Default: False
            use_all : boolean
                Flag if all chasers are allowed to make a action (for house rules)
                Default: False

            Returns
            ----------
            list
                List with relative score changes ordered start team -> second team
        """
        score_change = [0,0]
        result_1 = {}
        result_2 = {}
        gamelogger.gamestep("{} Keeper".format(self.team_1_name))
        result_1 = self.keeper_action(self.teams[self.start_i]["Keeper"], team=self.team_1_name)
        # second team Keeper
        gamelogger.gamestep("{} Keeper".format(self.team_2_name))
        result_2 = self.keeper_action(self.teams[self.last_i]["Keeper"], team=self.team_2_name)
        score_change = [result_1["own"] + result_2["other"], result_1["other"] + result_2["own"]]
        self.score[self.start_i] += score_change[0]
        self.score[self.last_i] += score_change[1]
        return score_change


    def Seeker_turns(self):
        """
            Performes all Beater actions for one turn

            Parameters
            ----------
            single_roles : boolean
                Flag if only one beater and chaser of a team should roll
                Default: False
            use_all : boolean
                Flag if all chasers are allowed to make a action (for house rules)
                Default: False

            Returns
            ----------
            list
                List with relative score changes ordered start team -> second team
        """
        turn_change = [0,0,False,False]
        result_1 = {}
        result_2 = {}
        # first team Seeker
        gamelogger.gamestep("{} Seeker".format(self.team_1_name))
        result_1 = self.seeker_action(self.teams[self.start_i]["Seeker"], team=self.team_1_name)
        self.teams[self.start_i]["Seeker"]["temp"]
        if result_1["snitch"]:
            # check if snitch was cought
            self.snitch = True
            self.score[self.start_i] += 150
            turn_change[0] = 150
            turn_change[2] = True
            self.ending_team = self.teams[self.start_i]["Name"]
        elif result_1["streak"] < 0:
            self.teams[self.start_i]["Seeker"]["temp"] = result_1["streak"]
            self.teams[self.start_i]["Seeker"]["streak"] = 0
        else: 
            self.teams[self.start_i]["Seeker"]["streak"] = result_1["streak"]
        # second team Seeker
        if not self.snitch:
            gamelogger.gamestep("{} Seeker".format(self.team_2_name))
            result_2 = self.seeker_action(self.teams[self.last_i]["Seeker"], team=self.team_2_name)
            self.teams[self.last_i]["Seeker"]["temp"] = 0
            if result_2["snitch"]:
                self.snitch = True
                self.score[self.last_i] += 150
                self.ending_team = self.teams[self.last_i]["Name"]
                turn_change[1] = 150
                turn_change[3] = True
            elif result_2["streak"] < 0:
                self.teams[self.last_i]["Seeker"]["temp"] = result_2["streak"]
                self.teams[self.last_i]["Seeker"]["streak"] = 0
            else:
                self.teams[self.last_i]["Seeker"]["streak"] = result_2["streak"]
        # tally up changes:
        return turn_change


    def run_game(self, single_roles=False, use_weather=False):
        """
            Performs quidditch player actions until the snitch is cought

            Parameters
            ----------
            single_roles : boolean
                Flag if only one beater and chaser of a team should roll
                Default: False
            use_weather : boolean
                Flag if game metadata should be collected.
                Default: False
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
        self.single_roles = single_roles
        self.use_weather = use_weather

        # set up game variables
        self.snitch = False

        # Pre game loop rolls
        self.pre_game(use_weather)
        
        # run game simulation
        while not self.snitch:
            self.game_turns += 1
            # Chaser Actions
            self.chaser_turns()
            # Beater Actions
            self.beater_turns()
            # Keeper Actions
            self.keeper_turns()
            # Seeker Actions
            self.Seeker_turns()
            # ensure no team is below 0 points
            self.score = [max(i,0) for i in self.score]
            # end of round logs
            gamelogger.gamestep("\nRound {} Score Summary".format(self.game_turns))
            gamelogger.gamestep("{}: {} - {}: {}\n".format(self.teams[0]["Name"], self.score[0], self.teams[1]["Name"], self.score[1]))
            logger.info("Turn {} Score: {} - {}".format(self.game_turns, self.score[0], self.score[1]))
        # Post Game 
        # verbose Scores
        scores = {
            self.teams[0]["Name"]: self.score[0],
            self.teams[1]["Name"]: self.score[1]
        }
        # build Result object
        self.game_results = {
            "ending_team": self.ending_team,
            "game_turns": self.game_turns,
            "score": scores,
            "start_team": self.team_1_name,
            "weather": self.weather
        }
        if self.player_results:
            self.game_results["player_results"] = self.player_results
        
        # send basic info to default logger
        logger.info("\nMatch Finished after {} turns".format(self.game_turns))
        logger.info("{} ended the Match".format(self.ending_team))
        logger.info("Final Score: {} - {}".format(self.score[0],self.score[1]))

        # send in depth info to game logger
        gamelogger.gamestep("\n{} ended the Game!".format(self.ending_team))
        gamelogger.gamestep("Final Score:")
        gamelogger.gamestep("{} {} - {} {}".format(self.teams[0]["Name"], self.score[0], self.teams[1]["Name"], self.score[1]))
        self.score = scores
        return self.game_results


class Modified_Game(Base_game):

    seeker_target = [0,0]

    def __init__(self, name, team_file=None):
        super(Modified_Game,self).__init__(name,team_file)


    def sum_modifyer(self, player, weather=None):
        """
            Sums up all modifyer aplying to a player

            Parameters
            ----------
            player : dict
                Player modifyer collection
            weather : int
                Weather modifyer. leave empty to use default game weather modifyer

            Returns
            ---------- 
            int
                sum of all modifyer
        """
        mods = player["base"] + player["mod"] + player["temp"]
        if weather:
            mods += weather
        if player.get("streak", None):
            mods += player["streak"]
        else:
            mods += self.weather
        return  mods


    def beater_target_seeker(self, beaters, active=0, team=None):
        """
            Performs the Beater House Rule action target Seeker
            
            Parameters
            ----------
            beaters : list
                List of Beater Modifyer collection (dict)
            active : int
                index of Beater taking the turn. leave empty when you only use one
            team : str
                Name of team for player stat tracking

            Returns
            ----------
            dict
                Collection of temporary seeker modifyer.
                Dict Parameter: 
                own : int
                    temp modifyer for own seeker player
                other : int
                    temp modifyer for other seeker player
                other_points : relative change of other points
        """
        # chooses the modifyer of the active player alternating between beaters
        stats = beaters[active]
        # roll with player stats + long term modifyers and one time temporary ones and weather if applied
        roll = self.dice_roll(stats["base"] + stats["mod"] + stats["temp"] + self.weather) 
        # get player name
        name = beaters[active].get("Name", "Beater" + str(active))
        # relative score changes
        game = {"own": 0, "other": 0, "other_points": 10}
        status = None
        gamelogger.gamestep("{} targets enemy Seeker".format(name))
        gamelogger.gamestep("A enemy chaser slip through and scores!")
        if roll >= 10:
            game["other"] = -2
            status = 2
            gamelogger.gamestep("{}: Success.")
            gamelogger.gamestep("A Nasty Hit")
        elif roll >= 7:
            game["other"] = -1
            status = 1
        else:
            game["own"] = -1
            status = 1
        if self.get_metadata:
            self.add_track_record(name, status, team)
        return game


    def beater_turns(self, single_roles=False, use_all=False):
        """
            Performes all Beater actions for one turn

            Parameters
            ----------
            single_roles : boolean
                Flag if only one beater and chaser of a team should roll
                Default: False
            use_all : boolean
                Flag if all chasers are allowed to make a action (for house rules)
                Default: False

            Returns
            ----------
            list
                List with relative score changes ordered start team -> second team
        """
        score_change = [0,0]
        # when all player should be used invoke function recurively
        if use_all:
            for index in self.teams[self.start_i]["Beater"]:
                changes = self.chaser_turns(single_roles=True)
                score_change[0] += changes[0]
                score_change[1] += changes[1]
                index = (index + 1) %len(self.teams[self.start_i]["Beater"])
        else:
            # temp result variables
            result_1 = {}
            result_2 = {}
            # first team Beater
            gamelogger.gamestep("{} Beater".format(self.team_1_name))
            # check if beater targets seeker instead of normal action
            if self.sum_modifyer(self.teams[self.last_i]["Seeker"]) >= 4:
                # and self.dice_roll() > 5 + self.seeker_target[self.last_i]
                result_1 = self.beater_target_seeker(self.teams[self.start_i]["Beater"], self.next_beater[self.start_i], team=self.team_1_name)
                self.teams[self.start_i]["Seeker"]["temp"] += result_1["own"]
                self.teams[self.last_i]["Seeker"]["temp"] += result_1["other"]
                result_1["own"] = 0
                result_1["other"] = result_1["other_points"]
                logger.error(self.teams[self.start_i]["Seeker"])
                logger.error(self.teams[self.last_i]["Seeker"])
                # reduce chance to target seeker again
                self.seeker_target[self.last_i] += 2
            else:
                result_1 = self.beater_action(self.teams[self.start_i]["Beater"], self.next_beater[self.start_i], team=self.team_1_name)
                # increase chance to target seeker toward base value
                if self.seeker_target[self.last_i] > 0:
                    self.seeker_target[self.last_i] -= 1
            if not single_roles:
                self.next_beater[self.start_i] = (self.next_beater[self.start_i] + 1) % len(self.teams[self.start_i]["Beater"])
            # second team Beater
            gamelogger.gamestep("{} Beater".format(self.team_2_name))
            # check if beater targets seeker instead of normal action
            if self.sum_modifyer(self.teams[self.start_i]["Seeker"]) >= 4:
                result_2 = self.beater_target_seeker(self.teams[self.start_i]["Beater"], self.next_beater[self.start_i], team=self.team_1_name)
                self.teams[self.last_i]["Seeker"]["temp"] += result_1["own"]
                self.teams[self.start_i]["Seeker"]["temp"] += result_1["other"]
                result_2["own"] = 0
                logger.error(result_2)
                result_2["other"] = result_1["other_points"]
                # reduce chance to target seeker again
                self.seeker_target[self.start_i] += 2
            else:
                result_2 = self.beater_action(self.teams[self.last_i]["Beater"], self.next_beater[self.last_i], team=self.team_2_name) 
                # increase chance to target seeker toward base value
                if self.seeker_target[self.start_i] > 0:
                    self.seeker_target[self.start_i] -= 1
            if not single_roles:
                self.next_beater[self.last_i] = (self.next_beater[self.last_i] + 1) % len(self.teams[self.last_i]["Beater"])
            score_change = [result_1["own"] + result_2["other"], result_1["other"] + result_2["own"]]
            self.score[self.start_i] += score_change[0]
            self.score[self.last_i	] += score_change[1]
            return[score_change]




if __name__ == "__main__":
    args = parser.parse_args()
    # load team file
    try:
        # create game with file name as game name
        name = str(args.team_file).rsplit(sep='/', maxsplit=1)[-1].rsplit(sep='.',maxsplit=1)[0]
        game = None
        if args.house_rules:
            game = Modified_Game(name)
        else:
            game = Base_game(name)
        teams = game.load_teams(args.team_file)

        # setup logging parameter
        add_game_logging()
        gamelogger = logging.getLogger("GameLogger")
        gamelogger.setLevel(15)
        if args.collect_metadata:
            # setup log file handler
            game.get_metadata = args.collect_metadata
            gamehandler = logging.FileHandler("{}.txt".format(game.name))
            gamelogger.addHandler(gamehandler)
        # run game
        result = game.run_game(single_roles=args.single_roles, use_weather=args.use_weather)
        # dump result into file
        with open("{}_result.json".format(game.name),mode="w") as result_file:
            json.dump(result, result_file, sort_keys=True, indent=4)
    except FileNotFoundError as e:
        logger.error(e)
        logger.error("\tCheck your file name and location!")
    except IndexError as e2:
        logger.error(e2)
        logger.error("\tCheck if your team file contains 2 teams")
        logger.error("\tif so please open a issue containing following error message at:")
        logger.error("\thttps://github.com/darkmeadow/quidditch_simulator/issues")
        logger.error(e2,stack_info=True)