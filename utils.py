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

def process_lichess_game_dict(game_dict, username):
    """
    Processes a single game dictionary, as it comes from the result of `lichess.api.user_games()`.
    """

    # get opening info
    opening_name = game_dict["opening"]["name"]
    opening_name_simple = opening_name.split(':')[0]
    opening_code = game_dict["opening"]["eco"]

    # get color
    if 'aiLevel' in game_dict["players"]["white"].keys():
        color = "black"
    elif 'aiLevel' in game_dict["players"]["black"].keys():
        color = "white"
    elif game_dict["players"]["white"]["user"]["name"]==username:
        color = "white"
    else:
        color = "black"

    # get points
    if "winner" not in game_dict:
        points = .5
    elif game_dict["winner"]==color:
        points = 1
    else:
        points = 0

    # return
    return {"opening_name": opening_name,
            "opening_name_simple": opening_name_simple,
            "opening_code": opening_code, 
            "color": color,
            "points": points}

def is_legal_lichess_game(game_dict):
    """
    Not all games have all requisite data. If they don't, return False; else, return True.
    """
    if "opening" in game_dict:
        return True
    return False

def get_lichess_user_games_df(lichess_username, num_games):
    """
    Get all the formatted lichess gamese of a lichess user.

    Note on the maximum speed of this function
    (from https://lichess.org/api#operation/apiGamesUser):
        "The game stream is throttled, depending on who is making the request:
            - Anonymous request: 20 games per second
            - OAuth2 authenticated request: 30 games per second
            - Authenticated, downloading your own games: 60 games per second"
    """
    query = {
        "opening": True,
        "moves": False,
        "sort": "dateDesc",
        "max": num_games}
    games = [process_lichess_game_dict(g, lichess_username)
            for g in lichess.api.user_games(lichess_username, **query)
            if is_legal_lichess_game(g)]
    return pd.DataFrame(games)

def get_user_opening_stats(lichess_username, num_games):
    """
    Get the opening statistics of a given user.

    Returns a 2-tuple (pd.DataFrame of white opening stats, pd.DataFrame of black opening stats)
    """
    lichess_games_df = get_lichess_user_games_df(lichess_username, num_games)
    opening_stats = {
        color: (lichess_games_df
                [lichess_games_df["color"]==color]
                .groupby("opening_name_simple")
                ["points"]
                .agg(["count", "mean"])
                .sort_values("count", ascending=False)
                .head(5)
                .reset_index()
                .rename({"opening_name_simple": "opening",
                         "count": "num_games",
                         "mean": "avg_points_per_game"},
                        axis=1)
                .to_dict("records"))
        for color in ["white", "black"]}
    return opening_stats

def is_lichess_user(lichess_username):
    """
    Check if a user exists on lichess.
    """
    try:
        user = lichess.api.user(lichess_username)
        return True
    except lichess.api.ApiHttpError:
        return False

def get_chesscom_user_games_df(chesscom_username, start_date):
    """
    Get all the formatted chess.com games of a chess.com user.
    """
    pass


# main
if __name__=="__main__":

    # load the games
    user = 'normanrookwell'
    print(get_lichess_user_opening_stats(user, 10))