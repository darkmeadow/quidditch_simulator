# Datatype explanations

## Table of Contents

- [Player](#Player_object)
- [Team](#Team_object)
- [Match](#matchobject)

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
        "Name": "SomeName",
        ...
    },
    {
        "Name": "SomeOtherName",
        ...
    }
]
```