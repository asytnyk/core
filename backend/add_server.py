#!/usr/bin/env python

""" Generates an uuid, saves to DB, and prints it """

import argparse, ConfigParser, sqlite3, time, sys, hashlib, uuid

config = ConfigParser.ConfigParser()
config.read("backend.conf")
db_file = config.get("db", "file")

db = sqlite3.connect(db_file)

SERVER_ADD_QUERY = """
    INSERT INTO server(server_uuid, customer_uuid, activation_uuid, ssh_key_uuid, vpn_key_uuid)
    values (?,?,?,?,?)
"""

def main():
    server_uuid = str(uuid.uuid4())

    parser = argparse.ArgumentParser()
    parser.add_argument('--activation', type=str)
    parser.add_argument('--customer', type=str)
    parser.add_argument('--ssh', type=str)
    parser.add_argument('--vpn', type=str)
    args = parser.parse_args()

    if not args.activation or not args.customer or not args.ssh or not args.vpn:
        print "Error, some argument(s) missing"
        sys.exit()

    c = db.cursor()
    c.execute("PRAGMA foreign_keys=ON");
    c.execute(SERVER_ADD_QUERY, (server_uuid, args.customer, args.activation,
        args.ssh, args.vpn))

    db.commit()
    db.close()

if __name__ == "__main__":
    main()
