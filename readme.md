# Witchcraft & Wizzardry Quidditch Simulator

A Quidditch game simulator based on Wackstevens [Witchcraft and Wizzardry](tablestory.tv/waw) System:

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [ToDo](#todo)
- [Credits](#credits)

## Installation

Clone repository into local working directory

## Usage

### Requirements

create a Match json file containing two team jsons as a list

+ Create and open a new .json file
+ Add two teams (see Example_team.json) into the file in list format
```json
[{Name: "TeamName", ...}, {Name: "Teamname", ...}]
```
Optionally:

+ add bonuses/pentalties modifyer to each players base value

+ add Player Names for each player

### Command line


1. In commandline use:

    ```cmd
    python -m quidditch.py --team-file Path/to/file/[filename].json
    ```
    + If you want to simulate weather effects add
        ```
        --use_weather
        ```

    + If you want to simulate weather effects add
        ```
        --use_weather
        ```
        
    + To return a more in depth game log add
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

+ Simulate seasons/leagues

+ Web interface to create/maintain quidditch teams

+ Verbose gamelogs to get a condenced game review

+ Analyze Game/ season outcomes

+ Add house rules

## Credits

### Thank you to
+ Wacksteven for creating the system [tablestory.tv/waw](tablestory.tv/waw)
+ Kujio for building the discord bot that inspired this simulation
+ Last-Socratic for hist quidditch analyser and code insight
