# NOTES:
# it might be easier to write my own parser. python-lichess does it themselves, using these lines of code:
# https://github.com/cyanfish/python-lichess/blob/8deea5dda8965b90915c744d65f2a4bc3ee085e5/lichess/api.py#L293
# https://github.com/cyanfish/python-lichess/blob/8deea5dda8965b90915c744d65f2a4bc3ee085e5/lichess/api.py#L89
# there's something with specifying the object_type=lichess.format.GAME_STREAM_OBJECT and passing it to the parser

import pandas as pd
import lichess.api
import requests

# we want to create a table for user's games, that stores: color, points-earned, opening
def process_game_dict(game_dict, username):
    """
    Processes a single game dictionary, as it comes from the result of lichess.api.user_games().
    """
    opening_name = game_dict["opening"]["name"]
    opening_name_simple = opening_name.split(':')[0]
    opening_code = game_dict["opening"]["eco"]
    color = "white" if game_dict["players"]["white"]["user"]["id"]==username else "black"
    if "winner" not in game_dict:
        points = .5
    elif game_dict["winner"]==color:
        points = 1
    else:
        points = 0
    return {"opening_name": opening_name,
            "opening_name_simple": opening_name_simple,
            "opening_code": opening_code, 
            "color": color,
            "points": points}

# load the games
user = 'madmaxmatze'
query = {
    "opening": True,
    "moves": False,
    "sort": "dateDesc",
    # "max": 300
    }
games = [process_game_dict(g, user) for g in lichess.api.user_games(user, **query)]

# test
games = pd.DataFrame(games)
print(games.head(5))
for color in ["white", "black"]:
    display_games = \
        (games
         [games["color"]==color]
         .groupby("opening_name_simple")
         ["points"]
         .agg(["count", "mean"])
         .sort_values("count", ascending=False)
         .rename({"opening_name_simple": "opening", "count": "num_games", "mean": "avg_points_per_game"})
         .head(10))
    print(display_games)