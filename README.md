# Project: Data modelling with postgres
## 1.Project description 
This project is a homework for Udacity Data Engineering Nanodegree Program. The task is to model relational database structure and to develop etl script that accomplishes import from JSON files into that database. There are two types of incoming JSONs. The first one is a kind of songs dictionary that contains song attributes like song name and artist. The second one is a log of user session describing user actions on different pages of music player. The purpose of the whole project is to give ability to a business analyst to write simple queries against a well structured data to find user beheivier patterns. Like "what and when should we do to stop them unsubscribing". 

## 2.Database design
Database structure is defined at **sql_queries.py** by CREATE TABLE statements. Following tables are created for that project:

### 2.1 Fact Table 
> **songplays** - records in log data associated with song plays i.e. records with page NextSong
> songplay_id, start_time, user_id, level, song_id, artist_id, session_id, location, user_agent

### 2.2 Dimension Tables

> **users** - users in the app
> user_id, first_name, last_name, gender, level

> **songs** - songs in music database
> song_id, title, artist_id, year, duration

> **artists** - artists in music database
> artist_id, name, location, latitude, longitude

> **time** - timestamps of records in songplays broken down into specific units
> start_time, hour, day, week, month, year, weekday

### 2.3 ER model

![alt text](https://github.com/eruslan/SongsDataModel/blob/master/sparkifydb_erd.png)

## 3. ETL Process
The ETL process is performed by the **etl.py** python script.

### 3.1 ETL Input - Songs data
The songs dataset is at **data\songs_data** directory and its subderrictories. 

Path example: song_data/A/B/C/TRABCEI128F424C983.json

File structure example:

```javascript
{"num_songs": 1, 
"artist_id": "ARJIE2Y1187B994AB7",
"artist_latitude": null,
"artist_longitude": null, 
"artist_location": "",
"artist_name": "Line Renaud", 
"song_id": "SOUPIRU12A6D4FA1E1",
"title": "Der Kleine Dompfaff",
"duration": 152.92036,
"year": 0}
```
### 3.2 ETL Input - Logs data
Logs dataset is at **\data\log_data** directory and its subderrictories.

Path example: log_data/2018/11/2018-11-12-events.json

File structure example:
```javascript
{"artist":"Mr Oizo",
"auth":"Logged In",
"firstName":"Kaylee",
"gender":"F",
"itemInSession":3,
"lastName":"Summers",
"length":144.03873,
"level":"free",
"location":"Phoenix-Mesa-Scottsdale, AZ",
"method":"PUT",
"page":"NextSong",
"registration":1540344794796.0,
"sessionId":139,
"song":"Flat 55",
"status":200,
"ts":1541106352796,
"userAgent":"\"Mozilla\/5.0 (Windows NT 6.1; WOW64) AppleWebKit\/537.36 (KHTML, like Gecko) Chrome\/35.0.1916.153 Safari\/537.36\"",
"userId":"8"}
```

### 3.3 ETL Flow
The import sequence of **etl.py** is following
1. For each file at songs_data inserts into **songs** and **artists** table are performed. Commit is done after each file processed.
2. For each file at log_data:
    1. **Time** table insert performed
    2. **Users** table insert performed
    3. For each record at log file a select query to **songs** and **artists** table performed to get artist_id and song_id. That data is accomulated and then inserted into **songplays** table together with all the other fields at one batch. Commit is done after each file processed  

### 3.4 Attribute mapping  

| Origin     | OriginField : SampleData                                                                                                                                                          | Destanation<br>table.column               | Comment                                                                                                                                |
| ---------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| song\_data | "num\_songs": 1                                                                                                                                                                   | None                                      | excluded from import                                                                                                                   |
| song\_data | "artist\_id": "ARMAC4T1187FB3FA4C",                                                                                                                                               | artists.artist\_id<br>songs.artist\_id    | varchar. PRIMARY KEY for artists table                                                                                                 |
| song\_data | "artist\_latitude": 40.82624,                                                                                                                                                     | artists.latitude                          | float                                                                                                                                  |
| song\_data | "artist\_longitude": -74.47995,                                                                                                                                                   | artists.longitude                         | float                                                                                                                                  |
| song\_data | "artist\_location": "Morris Plains, NJ",                                                                                                                                          | artists.location                          | varchar                                                                                                                                |
| song\_data | "artist\_name": "The Dillinger Escape Plan",                                                                                                                                      | artists.name                              | varchar                                                                                                                                |
| song\_data | "song\_id": "SOBBUGU12A8C13E95D",                                                                                                                                                 | songs.song\_id                            | varchar PRIMARY KEY                                                                                                                    |
| song\_data | "title": "Setting Fire to Sleeping Giants",                                                                                                                                       | songs.title                               | varchar. Is used to map songplays to songs table with songplays.song\_id                                                               |
| song\_data | "duration": 207.77751,                                                                                                                                                            | songs.duration                            | float                                                                                                                                  |
| song\_data | "year": 2004                                                                                                                                                                      | songs .year                               | int                                                                                                                                    |
| log\_data  | "artist": "Alicia Keys",                                                                                                                                                          | artists.name                              | varchar. Is used to map songplays to artists table with songplays.artist\_id                                                           |
| log\_data  | auth: "Logged In",                                                                                                                                                                | None                                      | excluded from import                                                                                                                   |
| log\_data  | "userId": "26"                                                                                                                                                                    | users.user\_id<br>songplays.user\_id      | int. PRIMARY KEY for users table                                                                                                       |
| log\_data  | "firstName": "Ryan",                                                                                                                                                              | users.firstName                           | varchar                                                                                                                                |
| log\_data  | "gender": "M",                                                                                                                                                                    | users.gender                              | varchar                                                                                                                                |
| log\_data  | "itemInSession": 1,                                                                                                                                                               | None                                      | excluded from import                                                                                                                   |
| log\_data  | "lastName": "Smith",                                                                                                                                                              | users.lastName                            | varchar                                                                                                                                |
| log\_data  | "length": 216.47628,                                                                                                                                                              | None                                      | is used as additional condition during import to map songplays on songs with songs.duration                                            |
| log\_data  | "level": "free",                                                                                                                                                                  | users.level<br>songplays.level            | varchar                                                                                                                                |
| None       | None                                                                                                                                                                              | songplays.songplay\_id                    | int serial PRIMARY KEY                                                                                                                 |
| None       | None                                                                                                                                                                              | songplays.song\_id                        | varchar refference to songs.song\_id, is mapped by song, duration, and artist\_name from previusly loaded songs and artists tables     |
| None       | None                                                                                                                                                                              | songplays.artist\_id                      | varchar refference to artists.artist\_id, is mapped by song, duration, and artist\_name from previusly loaded songs and artists tables |
| log\_data  | "location": "San Jose-Sunnyvale-Santa Clara, CA",                                                                                                                                 | songplays.location                        | varchar                                                                                                                                |
| log\_data  | "method": "PUT",                                                                                                                                                                  | None                                      | excluded from import                                                                                                                   |
| log\_data  | "page": "NextSong",                                                                                                                                                               | None                                      | excluded from import                                                                                                                   |
| log\_data  | "registration": 1541016707796.0,                                                                                                                                                  | None                                      | excluded from import                                                                                                                   |
| log\_data  | "sessionId": 480,                                                                                                                                                                 | songplays.session\_id                     | int                                                                                                                                    |
| log\_data  | "song": "Empire State Of Mind (Part II) Broken Down",                                                                                                                             | songplays.song                            | varchar. Is used to map songplay to songs table                                                                                        |
| log\_data  | status: 200,                                                                                                                                                                      | None                                      | excluded from import                                                                                                                   |
| log\_data  | "ts": 1541979748796,                                                                                                                                                              | songplays.start\_time<br>time.start\_time | timestemp. PRIMARYKEY for time table                                                                                                   |
| log\_data  | songplay "userAgent": "\\"Mozilla\\/5.0 (X11; Linux x86\_64) AppleWebKit\\/537.36 (KHTML, like Gecko) Ubuntu Chromium\\/36.0.1985.125 Chrome\\/36.0.1985.125 Safari\\/537.36\\"", | songplays.user\_agent                     | varchar                                                                                                                                |
| None       | None                                                                                                                                                                              | time.hour                                 | pd.to\_datetime(df\['ts'\], unit='ms').hour                                                                                            |
| None       | None                                                                                                                                                                              | time.day                                  | pd.to\_datetime(df\['ts'\], unit='ms').day                                                                                             |
| None       | None                                                                                                                                                                              | time.week                                 | pd.to\_datetime(df\['ts'\], unit='ms').week                                                                                            |
| None       | None                                                                                                                                                                              | time.month                                | pd.to\_datetime(df\['ts'\], unit='ms').month                                                                                           |
| None       | None                                                                                                                                                                              | time.year                                 | pd.to\_datetime(df\['ts'\], unit='ms').year                                                                                            |
| None       | None                                                                                                                                                                              | time.weekday                              | pd.to\_datetime(df\['ts'\], unit='ms').weekday                                                                                         |

## 4. Project Repository files 

Folowing project files were provided as an input:

-**data\songs_data\**      Directory contains .json files with songs data. No changes applied

-**data\log_data\**        Directory contains .json files with user activity logs data. No changes applied

- __create_tables.py__       Run this script first to create local database and tabels. No changes applied. Following tables are created:
          
          - songplays  - user listening for the song session
          - songs - songs dictionary
          - artists - artists dictionary
          - useres - users dictionary
          - time - can be used to agregate songplays data by year,month,day e.t.c. 

- __sql_queries.py__         This scripts determis the set of SQL statements that are used in __create_tables.py__ and __etl.py__. There are statements to create, drop, insert tables and select statement to read songs data while processing user activity log. That file was modified. 
- __test.ipynb__ can be used to observe data in created tables. No changes applied.
- __etl.ipynb__ can be used to debug __etl.py__ code during development. Was modified by fullfilment of the empty parts.                       
- __etl.py__   Run this script to perform the import. There is no garantee that dublicates are not created when script is ran multiple times. Please always run  __create_tables.py__ before  __etl.py__ to avoid dublicates. If the song that user is lisstening to is not found in songs, then None will be added as artist and song. Actually only one song record is found at data provided.  __etl.py__ file was modified. 
- __sparkifydb_erd.png__ ER Diagramm

## 5. How To Run the Project

1. pip install following imports: 
          1. import os
          2. import glob
          3. import psycopg2
          4. import psycopg2.extras
          5. import pandas
          6. import time
          7. sql_queries  
2. initialise local Postres SQL installation with following connection string to be valid __"host=127.0.0.1 dbname=studentdb user=student password=student"__
3. Run create_tables.py
4. Run etl.py

## 6. Additional info

> With psycopg2.extras execute_batch **etl.py** script performance was x3 times improved (Thanks to instructor advice)

> UNLOGGED option added to CREATE TABLE statements for **songplays** and **time** tables seem to reduce 2 more seconds

> Following timing i'm getting at my workstation and it seems that most of it goes to file processing cause commenting of SQL statements dont give any improvement
```javascript
=========================================
Songs import durtion 2.556
Logs import duration 24.58
```
> Modified .py files were formated by autopep8 in VSCode.

> ER diagramm generated by https://pypi.org/project/sqlalchemy_schemadisplay/
