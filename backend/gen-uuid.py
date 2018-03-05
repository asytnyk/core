#!/usr/bin/env python

""" Generates an uuid, saves to DB, and prints it """

import ConfigParser, sqlite3, time, uuid

config = ConfigParser.ConfigParser()
config.read("backend.conf")
db_file = config.get("db", "file")

db = sqlite3.connect(db_file)

IACTIVATION_QUERY = """
    INSERT INTO activation(activation_uuid, activation_request_date, active) values (?, ?, ?)
"""

def main():
    myuuid = str(uuid.uuid4())

    # No need of more than one second of precision
    time_in_secs = int(time.time())

    c = db.cursor()
    c.execute(IACTIVATION_QUERY, (myuuid, time_in_secs, 0))

    db.commit()
    db.close()

    print myuuid

if __name__ == "__main__":
    main()
