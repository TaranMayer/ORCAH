"""
Responsible for interfacing with team database table
"""
import csv
import eclib.db.teams
import eclib.db.inspection
import echelpers as ech


async def load(db, file):
    """
    Load team profiles from registration CSV file

    :param db: database object
    :type db: ecdatabase.Database
    :param file: path to CSV file
    :type file: str
    """
    with open(file, newline='') as csvfile:
        reader = csv.DictReader(csvfile, quoting=csv.QUOTE_ALL)
        for row in reader:
            await db.upsert(eclib.db.teams.table_, {
                eclib.db.teams.team_num: row["Team"],
                eclib.db.teams.team_name: row["Name"],
                eclib.db.teams.organization: row["Organization"],
                eclib.db.teams.location: row["Region"]
            }, eclib.db.teams.team_num)
            await db.upsert(eclib.db.inspection.table_, {
                eclib.db.inspection.team_num: row["Team"]
            }, eclib.db.inspection.team_num)
