# Datatype explanations

## Table of Contents

- [Player](#Player_object)
- [Team](#Team_object)
- [Match](#Match_object)
- [Result](#Result_object) 

## Player_Object

A Player object contains all nessesary values for the simulation in addition a optional player name

+ a Json Object for all players should contain:

    ```
    {
        "base": 0, // Base atribute relevant to the role ranges from -2 to +3
        "mod":0, // Long term non weather modifyer (Injuries and other Conditions)
        "temp": 0 // modifyer only aplying to the next roll (inspirations)
    }
    ```

+ Seeker Character jsons also have to include a streak attribute

    ```
    {
        "base": 0, // Base atribute relevant to the role ranges from -2 to +3
        "mod": 0, // Long term non weather modifyer (Injuries and other Conditions)
        "streak": 0, // sum of all consecutive successes and partial successes
        "temp": 0 // modifyer only aplying to the next roll (inspirations)
    }
    ```

+ Optional all player objects can include a Name attribute

    ```json
    {
        "Name": "Masie Skyler",
        "base": 0,
        "mod": 0,
        "streak": 0,
        "temp": 0
    }
    ```

## Team_object

The Team object contains all player Objects needed for a simulation

```
 {
    "Name": "SomeName", // Team name is nessesary
    "Beater": [{...}],  // List with at least one player object
    "Chaser": [{...}],  // List with at least one player object
    "Keeper": {...},    // One Player object
    "Seeker": {...}     // One Player object with the streak attribute
}
```

Multiple Beater and Chaser player objects are optional
+ regular teams have 2 Beater and 3 Chaser
+ the simulation should be able to handle any amount of valid player objects

## Match_object

The match object is a simple Json object list containing 2 Team objects

```
[
    {
        "Name": "SomeTeamName",
        ...
    },
    {
        "Name": "SomeOtherTeamName",
        ...
    }
]
```

## Result_object:

The result object is a json containg following information:

```json
{
    "ending_team": "[TEAMNAME]",
    "game_turns": 5,
    "score": {
        "[TEAMNAME_HOME]": 123,
        "[TEAMNAME_GUEST]": 123,
    },
    "start_team": "[TEAMNAME]",
    "weather": 0
}
```
#### variable Reference:
+ ending_team: Name of the team whos Seeker cought the snitch

+ game_turns: Number of full game turns whith each two Chaser, Beater, Keeper and seeker actions.

+ score: Final Match scores.

+ start_team: Name of team starting each game turn (won the initiative roll in the beginning of the match)

+ weather: global weather modifyer for the game, usually ranges between -2 and 0


### Optional player_results

when metadata is collected a additional player_results object, that includes number indication on how succesfull they were each game turn (first to last action) will be included:

```json
{
    "player_results": {
        "[SOMETEAMNAME]": {
            "[PLAYERNAME|POSITION123]" : [
                0|1|2|3,
                0|1|2|3,
                0|1|2|3
            ],
            "[PLAYERNAME|POSITION123]": []
        },
        "[SOMEOTHERTEAMNAME]": {
            "[PLAYERNAME|POSITION123]" : [
                0|1|2|3,
                0|1|2|3,
                0|1|2|3
            ],
            "[PLAYERNAME|POSITION123]": []
        }
    }
}
```
#### Number reference:
+ 0 = Failure (rolled < 6)
+ 1 = Partial Success (rolled 7 - 9)
+ 2 = Success (rolled 10+, excluding seeker results with 15+)
+ 3 = Cought Snitch (Seeker rolled 15+)
