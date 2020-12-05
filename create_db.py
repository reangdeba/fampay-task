#!/usr/bin/python

# This program initiates db connection
# and creates tables if not created already.
# Sample usage: python create_db.py --name="videos.db"

# stabdard imports
import argparse
import sqlite3
from sqlite3 import Error

# open connection to a db file
def create_conn(db):
    """Open connection to a database file.
    e.g. filename videos.db
    """

    conn = None
    try:
        conn = sqlite3.connect(db)
        return conn
    except Error as e:
        print(e)

# create empty table initially
def create_table(conn, sql_statement):
    """
    Create a table given a connection to a database
    and valid SQL statement.
    """
    try:
        c = conn.cursor()
        c.execute(sql_statement)
    except Error as e:
        print(e)

# driver function to connect to a database
# create a new table as well
def main(database):

    # the table schema
    create_taylor_table = """ CREATE TABLE IF NOT EXISTS taylor (
        id integer PRIMARY KEY,
        title text NOT NULL,
        desc text,
        pubdate text,
        thumburls text
        ); """

    conn = create_conn(database)

    # create tables
    if conn is not None:
        # create table for Taylor Swift videos.
        # because why not?
        create_table(conn, create_taylor_table)
    else:
        print("Cannot create connection.")

if __name__ == '__main__':
    # accept CLI args
    parser = argparse.ArgumentParser()
    parser.add_argument('--name', help='Database name', default='videos.db')
    args = parser.parse_args()
    
    # create table!
    main(args.name)