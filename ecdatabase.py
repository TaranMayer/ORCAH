# Original code authored by and copyright 18x18az

# Changes made by and copyright Taran Mayer:
# Added a pair of functions to insert/delete things from a table in ways that weren't permitted with the existing functions
# Added functionality for a new table

"""
Provides 'Database' class:
Low-level database interaction and helper functions.
Abstracted further as appropriate in each module.
"""
import re
import sqlite3
import eclib.db.teams
import eclib.db.queue
import eclib.db.inspection
import eclib.db.skills
import eclib.db.chat
import eclib.db.matches
import ecmodules.set_match

class Database:
    """
    Low-level database interaction and helper functions.
    Abstracted further as appropriate in each module.
    """

    def __init__(self, db_file):
        """
        Database initialization function. Creates necessary tables.
        :param db_file: database file on disk
        :type db_file: str
        """
        def regexp(expr, item):
            """
            Allows comparison by regex in SQLite conditions (REGEXP function)
            """
            reg = re.compile(expr)
            return reg.search(item) is not None

        self.connection = sqlite3.connect(db_file)
        self.connection.row_factory = sqlite3.Row
        self.connection.create_function("REGEXP", 2, regexp)
        self.cursor = self.connection.cursor()
        if self.cursor is None:
            raise Exception("Error fetching database cursor!")

        self.cursor.execute(eclib.db.teams.create_)
        self.cursor.execute(eclib.db.queue.create_)
        self.cursor.execute(eclib.db.inspection.create_)
        self.cursor.execute(eclib.db.skills.create_)
        self.cursor.execute(eclib.db.chat.create_)
        self.cursor.execute(eclib.db.matches.create_)

        print("made db")


    async def insert(self, table, values):
        """
        Insert row of data into database table.

        :param table: database table
        :type table: str
        :param values: column names and their corresponding data to be written
        :type values: dict[str, T]
        :return: ROWID of newly inserted row
        :rtype: int
        """
        vals = list(values.items())
        inputs = list()
        statement = "INSERT INTO " + table + "(" + vals[0][0]
        for val in vals[1:]:
            statement += ", " + val[0]
        statement += ") VALUES(?"
        inputs.append(vals[0][1])
        for val in vals[1:]:
            statement += ",?"
            inputs.append(val[1])
        statement += ")"
        self.cursor.execute(statement, inputs)
        self.connection.commit()
        return self.cursor.lastrowid

    async def update(self, table, conditions, values):
        """
        Update row(s) of a database table matching the given condition(s).

        :param table: database table
        :type table: str
        :param conditions: SQLite condition expressions that must all be matched. Tuples consist of column name, operator, expression.
        :type conditions: list[tuple[str, str, T]]
        :param values: column names and their corresponding data to be written
        :type values: dict[str, T]
        """
        vals = list(values.items())
        inputs = list()
        statement = "UPDATE " + table + " SET " + vals[0][0] + "=?"
        inputs.append(vals[0][1])
        for val in vals[1:]:
            statement += ", " + val[0] + "=?"
            inputs.append(val[1])
        statement += " WHERE " + conditions[0][0] + " " + conditions[0][1] + " ?"
        inputs.append(conditions[0][2])
        for cond in conditions[1:]:
            statement += " AND " + cond[0] + " " + cond[1] + " ?"
            inputs.append(cond[2])
        self.cursor.execute(statement, inputs)
        self.connection.commit()
        print("updated table")

    async def upsert(self, table, values, conflict_target):
        """
        Upserts row of data into database table.

        :param table: database table
        :type table: str
        :param values: column names and their corresponding data to be written
        :type values: dict[str, T]
        :param conflict_target: column name whose failing uniqueness constraint triggers the update
        :type conflict_target: str
        :return: ROWID of newly inserted row
        :rtype: int
        """
        vals = list(values.items())
        inputs = list()
        statement = "INSERT INTO " + table + "(" + vals[0][0]
        for val in vals[1:]:
            statement += ", " + val[0]
        statement += ") VALUES(?"
        inputs.append(vals[0][1])
        for val in vals[1:]:
            statement += ",?"
            inputs.append(val[1])
        statement += ") ON CONFLICT(" + conflict_target + ") DO"
        statement += " UPDATE SET " + vals[0][0] + "=excluded." + vals[0][0]
        for val in vals[1:]:
            statement += ", " + val[0] + "=excluded." + val[0]
        self.cursor.execute(statement, inputs)
        self.connection.commit()
        return self.cursor.lastrowid

    async def select(self, table, conditions):
        """
        Fetch row(s) of a database table matching the given condition(s).

        :param table: database table
        :type table: str
        :param conditions: SQLite condition expressions that must all be matched. Tuples consist of column name, operator, expression.
        :type conditions: list[tuple[str, str, T]]
        :return: matching row(s)
        :rtype: list[dict[str, T]]
        """
        inputs = list()
        statement = "SELECT rowid, * FROM " + table
        if conditions:
            statement += " WHERE " + conditions[0][0] + " " + conditions[0][1] + " ?"
            inputs.append(conditions[0][2])
            for cond in conditions[1:]:
                statement += " AND " + cond[0] + " " + cond[1] + " ?"
                inputs.append(cond[2])
        self.cursor.execute(statement, inputs)
        rows = [dict(row) for row in self.cursor.fetchall()]
        return rows

    async def select_special(self, input):
        """
        Fetch row(s) of a database table matching the given condition(s).

        :param table: database table
        :type table: str
        :param conditions: SQLite condition expressions that must all be matched. Tuples consist of column name, operator, expression.
        :type conditions: list[tuple[str, str, T]]
        :return: matching row(s)
        :rtype: list[dict[str, T]]
        """
        self.cursor.execute(input)
        rows = [dict(row) for row in self.cursor.fetchall()]
        return rows

    async def delete(self, table, conditions):
        """
        Delete row(s) of a database table.

        :param table: database table
        :type table: str
        :param conditions: SQLite condition expressions that must all be matched. Tuples consist of column name, operator, expression.
        :type conditions: list[tuple[str, str, T]]
        """
        inputs = list()
        statement = "DELETE FROM " + table
        statement += " WHERE " + conditions[0][0] + " " + conditions[0][1] + " ?"
        inputs.append(conditions[0][2])
        for cond in conditions[1:]:
            statement += " AND " + cond[0] + " " + cond[1] + " ?"
            inputs.append(cond[2])
        self.cursor.execute(statement, inputs)
        self.connection.commit()
    async def delete_special(self, conditions):
        """
        Delete row(s) of a database table.

        :param table: database table
        :type table: str
        :param conditions: SQLite condition expressions that must all be matched. Tuples consist of column name, operator, expression.
        :type conditions: list[tuple[str, str, T]]
        """
        self.cursor.execute(conditions)
        self.connection.commit()
