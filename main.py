# NOTES:
# it might be easier to write my own parser. python-lichess does it themselves, using these lines of code:
# https://github.com/cyanfish/python-lichess/blob/8deea5dda8965b90915c744d65f2a4bc3ee085e5/lichess/api.py#L293
# https://github.com/cyanfish/python-lichess/blob/8deea5dda8965b90915c744d65f2a4bc3ee085e5/lichess/api.py#L89
# there's something with specifying the object_type=lichess.format.GAME_STREAM_OBJECT and passing it to the parser

# RESOURCES
# https://devcenter.heroku.com/articles/flask-memcache
# https://lichess.org/api#operation/apiUserCurrentGame

import pandas as pd
import lichess.api
import requests

def process_game_dict(game_dict, username):
    """
    Processes a single game dictionary, as it comes from the result of `lichess.api.user_games()`.
    """
    # print(game_dict)

    # get opening info
    opening_name = game_dict["opening"]["name"]
    opening_name_simple = opening_name.split(':')[0]
    opening_code = game_dict["opening"]["eco"]

    # get color
    if 'aiLevel' in game_dict["players"]["white"].keys():
        # print(1)
        color = "black"
    elif 'aiLevel' in game_dict["players"]["black"].keys():
        # print(2)
        color = "white"
    elif game_dict["players"]["white"]["user"]["name"]==username:
        # print(3)
        color = "white"
    else:
        # print(4)
        color = "black"

    # get points
    if "winner" not in game_dict:
        points = .5
    elif game_dict["winner"]==color:
        points = 1
    else:
        points = 0

    # return
    # print(color)
    return {"opening_name": opening_name,
            "opening_name_simple": opening_name_simple,
            "opening_code": opening_code, 
            "color": color,
            "points": points}

def is_legal_game(game_dict):
    """
    Not all games have all requisite data. If they don't, return False; else, return True.
    """
    if "opening" in game_dict:
        return True
    return False

if __name__=="__main__":

    # load the games
    user = 'normanrookwell'
    query = {
        "opening": True,
        "moves": False,
        "sort": "dateDesc",
        "max": 500}
    games = [process_game_dict(g, user)
            for g in lichess.api.user_games(user, **query)
            if is_legal_game(g)]

    # test
    games = pd.DataFrame(games)
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