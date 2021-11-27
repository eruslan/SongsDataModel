import os
import glob
import psycopg2
import pandas as pd
from sql_queries import *


def process_song_file(cur, filepath):
    """
    Reads the file in filepath and with help of cur cursor
    inserts data into songs and artists table. On errors prints errors.
    Input:
        cur - cursor
        filepath - string
    Return:
        None
    Output:
        info on errors
    """
    # open song file
    df = pd.read_json(filepath, lines=True)

    # insert artist record
    artist_data = df.loc[0]["artist_id"], \
        df.loc[0]["artist_name"], \
        df.loc[0]["artist_location"], \
        df.loc[0]["artist_latitude"], \
        df.loc[0]["artist_longitude"]
    try:
        cur.execute(artist_table_insert, artist_data)
    except psycopg2.Error as e:
        print("Error: Inserting artist")
        print(e)

    # insert song record
    song_data = df.loc[0]["song_id"], \
        df.loc[0]["title"], \
        df.loc[0]["artist_id"], \
        int(df.loc[0]["year"]), \
        df.loc[0]["duration"]
    try:
        cur.execute(song_table_insert, song_data)
    except psycopg2.Error as e:
        print("Error: Inserting song")
        print(e)


def process_log_file(cur, filepath):
    """
    Reads the file in filepath and with help of cur cursor
    inserts data into songplays, users and time table. On errors prints errors.
    Input:
        cur - cursor
        filepath - string
    Return:
        None
    Output:
        Info on errors
    """
    # open log file
    df = pd.read_json(filepath, lines=True)

    # filter by NextSong action
    df = df[df.page == 'NextSong']

    # convert timestamp column to datetime
    t = pd.to_datetime(df['ts'], unit='ms')

    # insert time data records
    time_data = pd.concat([df['ts'],
                           t.dt.hour,
                           t.dt.day,
                           t.dt.week,
                           t.dt.month,
                           t.dt.year,
                           t.dt.weekday],
                          axis=1)
    column_labels = ["ts", "hour", "day", "week", "month", "year", "weekday"]
    time_df = time_data.set_axis(column_labels, axis=1, inplace=False)

    for i, row in time_df.iterrows():
        cur.execute(time_table_insert, list(row))

    # load user table
    user_df = df.filter(['userId',
                         'firstName',
                         'lastName',
                         'gender',
                         'level'], axis=1
                        )

    # insert user records
    for i, row in user_df.iterrows():
        cur.execute(user_table_insert, row)

    # insert songplay records
    for index, row in df.iterrows():

        # get songid and artistid from song and artist tables
        cur.execute(song_select, (row.song, row.artist, row.length))
        results = cur.fetchone()

        if results:
            songid, artistid = results
        else:
            print("No entry in song_log for log_data {} {} {}".format(
                row.song, row.artist, row.length))
            songid, artistid = None, None

        # insert songplay record
        songplay_data = row.userId, \
            songid, \
            artistid, \
            row.sessionId, \
            row.ts, \
            row.level, \
            row.location, \
            row.userAgent
        cur.execute(songplay_table_insert, songplay_data)


def process_data(cur, conn, filepath, func):
    """
    Enlists JSON files in filepath dirrectory and calls func function against each file.
    cur cursor is passed to func function to operate with database data. 
    conn connection is used to commit transactions at the end 
    Input:
        cur - cursor
        conn - database connection
        filepath - string
        func - function to call against json files
    Return:
        None
    Output:
        Some print info about work done
    """
    # get all files matching extension from directory
    all_files = []
    for root, dirs, files in os.walk(filepath):
        files = glob.glob(os.path.join(root, '*.json'))
        for f in files:
            all_files.append(os.path.abspath(f))

    # get total number of files found
    num_files = len(all_files)
    print('{} files found in {}'.format(num_files, filepath))

    # iterate over files and process
    for i, datafile in enumerate(all_files, 1):
        func(cur, datafile)
        conn.commit()
        print('{}/{} files processed.'.format(i, num_files))


def main():
    """
    Sets up connection to local sparkifydb. Performs data processing 
    on songs and logs JSON files
    """
    conn = psycopg2.connect(
        "host=127.0.0.1 dbname=sparkifydb user=student password=student")
    cur = conn.cursor()

    process_data(cur, conn, filepath='data/song_data', func=process_song_file)
    process_data(cur, conn, filepath='data/log_data', func=process_log_file)

    conn.close()


if __name__ == "__main__":
    main()
