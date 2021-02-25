"""
Constants for 'skills' table
"""
match_num = "matchNum"
table_ = "matches"

team_red = "teamRed"
team_blue = "teamBlue"


red_score = "redScore"
blue_score = "blueScore"

red_auto = "redAuton"
blue_auto = "blueAuton"

red_wp = "redWinPoint"
blue_wp = "blueWinPoint"

wp_type_win = 1
wp_type_lose = 2

winner = "team"

referee = "referee"

scored = "scored"

create_ = "CREATE TABLE IF NOT EXISTS " + table_ + " ( " \
          + match_num + " INTEGER NOT NULL, " \
          + team_red + " TEXT NOT NULL, " \
          + team_blue + " TEXT NOT NULL, " \
          + red_score + " INTEGER NOT NULL, " \
          + blue_score + " INTEGER NOT NULL, " \
          + red_auto + " INTEGER NOT NULL, " \
          + blue_auto + " INTEGER NOT NULL, " \
          + red_wp + " INTEGER NOT NULL, " \
          + blue_wp + " INTEGER NOT NULL, " \
          + winner + " TEXT NOT NULL, " \
          + scored + " TEXT NOT NULL " \
          + ");"
