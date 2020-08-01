# Witchcraft & Wizzardry Quidditch Simulator

A Quidditch game Simulator based on Wackstevens [Witchcraft and Wizzardry](tablestory.tv/waw) System:



## installation

clone repository into local working directory

## Usage

### Requirements

create a Match json file containing two team jsons as a list

+ create and open a new .json file
+ Add two teams (see Example_team.json) into the file in list format
```json
[{Name: "TeamName", ...}, {Name: "Teamname", ...}]
```

### Command line


1. In commandline use:

    ```cmd
    python -m quidditch.py --team-file Path/to/file/[filename].json
    ```
    + if you want to simulate weather effects add
        ```
        --use_weather
        ```

    + if you want to simulate weather effects add
        ```
        --use_weather
        ```
    
    + to return a more in depth game log add
        ```
        --collect-metadata
        ```

2. Open the [teamname]_vs_[teamname]_result.json file to see the game results

### as Module

1. Import the quidditch.py into your module
2. Invoke load_teams to import match player data
    ```python
    load_teams(Path/to/file/[filename].json)
    ```
3. Invoke add_gamelog_level() to add the custom [loglevel](https://docs.python.org/3/library/logging.html#logging-levels) (GAMESTEP: 15)
    + you have to invoke the function even if you want to ignore gamestep messages

4. Invoke run_game() with the wanted parameter to start the simulation
    ```python
    run_game(teams, **kwargs)
    ```
    Optional arguments:
    1. use_duplicate_rolls : boolean
        + Flag if you want to alternate between chasers and beaters
        + Default: True 

    2. use_weather : boolean
        + Flag if you want to use weather calculations in the game 
        + Default: False


## ToDo

+ way to simulate seasons/leagues

+ web interface to create/maintain quidditch teams

+ verbose gamelogs to get a condenced game review

+ analyze Game/ season outcomes

+ add house rules

## Credits

### Thank you to
+ Wacksteven for creating the system [tablestory.tv/waw](tablestory.tv/waw)
+ Kujio for building the discord bot that inspired this simulation
+ Last-Socratic for hist quidditch analyser and code insight