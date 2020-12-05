# fampay-task

Requires `python=3.8`.

### Code layout
There are two files:

**Database initialization code.** `create_db.py` initializes a database file, and then creates a table in it. This table will be used later on to store the data we get from YouTube API. This part of the code is therefore concerned with just initializing the database and creating an empty new table.

**User interface.** This part of the code does the major work. The results would be served via a web server, which is just a simple Flask application. `serve.py` fetches data from the YouTube API, updates the table(s) we just created, and then displays it.

### Dependencies
There are several dependencies. The major ones are flask (the backbone), google-api-python-client (for getting YouTube data), sqlite3 for database, and apscheduler for running tasks periodically. You can install all of these through `pip`, e.g.:
```
$ conda create --name fampay python=3.8
$ conda activate fampay
$ pip install -r requirements.txt
```

It is recommended to use virtualenv or conda environments. However, this is optional.

### Workflow
This section will help you install the required libraries, get the relevant resources, so that we can have our API running. The workflow is (recommended to run in order)
1. **Install dependencies.** Install the required dependencies, following the guide outlined in the previous section.
2. **Get Developer key.** Visit [here](https://console.developers.google.com/apis/library/youtube.googleapis.com?id=125bab65-cfb6-4f25-9826-4dcc309bc508&project=quickstart-1556616853983) and [here](https://developers.google.com/youtube/v3/getting-started), and get an API key. Run `export DEVELOPER_KEY=[whatver-your-api-key]` in a terminal.
3. Run `create_db.py` to initialize our database and table(s) in it.
4. Finally, run `serve.py` to start the web server, wait about 20 seconds. Then, go to https://127.0.0.1:5000 to view the API.

By default the database stores latest search results for `taylor swift`. However, we can tweak a little bit and get results for any query term.
