#!/usr/bin/env python

""" Generates an uuid, saves to DB, and prints it """

import ConfigParser, sqlite3, uuid

config = ConfigParser.ConfigParser()
config.read("backend.conf")
db_file = config.get("db", "file")

db = sqlite3.connect(db_file)

def main():
    myuuid = uuid.uuid4()
    print myuuid

if __name__ == "__main__":
    main()
