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

def add_server(customer_uuid, activation_uuid, ssh_uuid, vpn_uuid):

    server_uuid = str(uuid.uuid4())

    if not server_uuid or not customer_uuid or not activation_uuid or not ssh_uuid or not vpn_uuid:
        raise ValueError('Argument(s) missing', server_uuid, customer_uuid, activation_uuid,
                ssh_uuid, vpn_uuid)

    c = db.cursor()
    c.execute("PRAGMA foreign_keys=ON");
    c.execute(SERVER_ADD_QUERY, (server_uuid, customer_uuid, activation_uuid, ssh_uuid, vpn_uuid))

    db.commit()
    db.close()

    return server_uuid

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--activation', type=str, help='activation uuid')
    parser.add_argument('--customer', type=str, help='customer uuid')
    parser.add_argument('--ssh', type=str, help='ssh_key uuid')
    parser.add_argument('--vpn', type=str, help='vpn_key uuid')
    args = parser.parse_args()

    if not args.activation or not args.customer or not args.ssh or not args.vpn:
        raise ValueError('Argument(s) missing', args.activation, args.customer, args.ssh, args.vpn)

    server_uuid = add_server(args.customer, args.activation, args.ssh, args.vpn)

    print "server_uuid: " + server_uuid

if __name__ == "__main__":
    main()
