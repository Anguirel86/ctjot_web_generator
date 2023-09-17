#!/usr/bin/env python3
import argparse
import io
import os
import pickle
import psycopg2
import sqlite3
from sqlite3 import Error
import sys

# Add the randomizer to the system path here.
# Use the path within the web generator container.
sys.path.append('/home/ctjot/web/jetsoftime/sourcefiles')

import randomizer


def create_connection() -> sqlite3.Connection:
    """
    Get a connection to the ctjot database.

    :return: database connection
    """
    conn = None
    try:
        if os.environ['DATABASE'] == "postgres":
            # Get the Postgres credentials from environment variables
            database = os.environ['POSTGRES_DB']
            user = os.environ['POSTGRES_USER']
            password = os.environ['POSTGRES_PASSWORD']
            host = os.environ['SQL_HOST']
            port = os.environ['SQL_PORT']
            conn = psycopg2.connect(database=database, user=user, password=password, host=host, port=port)
        else:
            # Not using Postgres.  Try to fall back to sqlite.
            conn = sqlite3.connect('./db.sqlite3')
    except Error as e:
        print(e)

    return conn


def get_seed_list(conn: sqlite3.Connection, count: int = 5):
    """
    Get a list of seeds.  Default to last 10, but allow more
    :param conn: Database connection to use
    :param count: Number of seeds to list
    """
    cur = conn.cursor()
    cur.execute("SELECT * FROM generator_game ORDER BY id DESC LIMIT " + str(count))

    rows = cur.fetchall()

    with open(str("ct.sfc"), 'rb') as infile:
        rom = bytearray(infile.read())

    for row in reversed(rows):
        share_id = row[1]
        creation_time = row[4]
        race_seed = row[5]
        settings = pickle.loads(row[2])
        config = pickle.loads(row[3])
        rando = randomizer.Randomizer(rom, True, settings, config)
        buffer = io.StringIO()
        print(f'share_id: {share_id}, created: {creation_time}, race_seed: {race_seed}')
        buffer.write("Seed: " + settings.seed + "\n")
        rando.write_settings_spoilers(buffer)
        print(buffer.getvalue())


def dump_spoiler_log(conn: sqlite3.Connection, share_id: str):
    """
    Dump a spoiler log for the seed with the given share id.

    :param conn: database connection object
    :param share_id: share id of the seed in question
    """
    cur = conn.cursor()
    cur.execute("SELECT * FROM generator_game WHERE share_id ='" + share_id + "'")

    rows = cur.fetchall()

    with open(str("ct.sfc"), 'rb') as infile:
        rom = bytearray(infile.read())

    for row in rows:
        settings = pickle.loads(row[2])
        config = pickle.loads(row[3])
        rando = randomizer.Randomizer(rom, True, settings, config)
        output = io.StringIO()
        rando.write_spoiler_log(output)

        # Dump the spoiler log data to stdout.
        print(output.getvalue())
        output.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--list', '-l', type=int, required=False, help="lists most recent seeds")
    parser.add_argument('--dump', '-d', type=str, required=False, help="dump a spoiler log for the given share id")
    args = parser.parse_args()

    conn = create_connection()
    with conn:
        if args.list:
            get_seed_list(conn, args.list)
        elif args.dump:
            dump_spoiler_log(conn, args.dump)
        else:
            parser.print_help()


if __name__ == '__main__':
    main()
