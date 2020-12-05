#!/usr/bin/python

# This program initiates db connection
# and creates tables if not created already.
# Sample usage: python serve.py

# standard imports
import os
import sys
import flask
from flask import request, jsonify
import sqlite3
from sqlite3 import Error
import time
import atexit
import argparse

# this runs a portion of the code continuously 
from apscheduler.schedulers.background import BackgroundScheduler

# google-api-python-client
# based on https://github.com/youtube/api-samples/blob/07263305b59a7c3275bc7e925f9ce6cabf774022/python/search.py
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

app = flask.Flask(__name__)
app.config["DEBUG"] = True


if os.environ['DEVELOPER_KEY']:
    DEVELOPER_KEY = os.environ['DEVELOPER_KEY']
else:
    sys.exit("Please provide DEVELOPER_KEY")

YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'

youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
developerKey=DEVELOPER_KEY)

# this fetches data from YT
# called continuously with the help of BackgroundScheduler
def fetch_data(q):
    # get videos published in the last two days
    search_response = youtube.search().list(
    publishedAfter='2020-12-03T13:44:50+00:00', # datetime in RFC 3339 format
    q=q,
    part='id, snippet',
    maxResults=10
    ).execute()

    videos = []

    for search_result in search_response.get('items', []):
        if search_result['id']['kind'] == 'youtube#video':
            title = search_result['snippet']['title']
            description = search_result['snippet']['description']
            pub_datetime = search_result['snippet']['publishedAt']
            thumb_url = search_result['snippet']['thumbnails']['high']["url"]
            videos.append((title, description, pub_datetime, thumb_url))
    
    return videos

# nothing much going on here
# just create a connection to the database
def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)

    return conn

# insert the fetched data to the database
# does not insert if already exists in the database
def insert_data(conn, videos):
    """
    Insert a set of 10 videos, if not already in the database
    """
    cur = conn.cursor()
    sql = ''' INSERT INTO taylor(title, desc, pubdate, thumburls)
              VALUES(?, ?, ?, ?) '''
    
    # insert a set of 10 videos, if not already in the database
    for video in videos:
        exists = 0
        for row in cur.execute("SELECT title FROM taylor WHERE title=?", (video[0],)):
            exists = row
            break
        if not exists:
            cur.execute(sql, video)
            conn.commit()
        else:
            continue
    return cur.lastrowid

# driver fucntion to continuously fetch and 
# insert data into the database
def main(database, q):
    conn = create_connection(database)
    
    videos = fetch_data(q)
    with conn:
        insert_data(conn, videos)

# helper fucntion to make fetching data from local db easier
def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

# default homepage
# nothing much here, redirects to API page
@app.route('/', methods=['GET'])
def home():
    return '''<h1>Fampay API</h1>
<p>Test API for Fampay Backend Intern Task.</p>
<p>Go to <a href="/api/taylor/all">/api/taylor/all</a></p>
<p>Or go to <a href="/api/taylor?id=1">/api/taylor?id=1</a> 1, 2, 3, and so on.</p>
'''

# display all records
@app.route('/api/taylor/all', methods=['GET'])
def api_all():
    conn = sqlite3.connect('videos.db')
    conn.row_factory = dict_factory
    cur = conn.cursor()
    all_videos = cur.execute('SELECT * FROM taylor ORDER BY pubdate DESC;').fetchall()

    return jsonify(all_videos)


# just a cheap 404 page.
@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The resource could not be found. :(</p>", 404

# serve records of for specific id
# url is of the form http://127.0.0.1:5000/api/taylor?id=1
@app.route('/api/taylor', methods=['GET'])
def api_filter():
    query_parameters = request.args

    id = query_parameters.get('id')

    query = "SELECT * FROM taylor WHERE"
    to_filter = []

    if id:
        query += ' id=? AND'
        to_filter.append(id)
    else:
        return page_not_found(404)

    query = query[:-4] + ';'

    conn = sqlite3.connect('videos.db')
    conn.row_factory = dict_factory
    cur = conn.cursor()

    results = cur.execute(query, to_filter).fetchall()

    return jsonify(results)


if __name__ == '__main__':
    # few CLI commands set up
    parser = argparse.ArgumentParser()
    parser.add_argument('--q', help='Search term', default='Taylor Swift')
    parser.add_argument('--database', help='Database name', default='videos.db')
    args = parser.parse_args()

    # fetch data from YouTube API
    # fetches new data every 20 seconds
    scheduler = BackgroundScheduler()
    scheduler.add_job(lambda: main(args.database, args.q), trigger="interval", seconds=20)
    scheduler.start()

    # serve the Flask app
    app.run(use_reloader=False)

    # stop fetching data from YT API after the app exits
    atexit.register(lambda: scheduler.shutdown())