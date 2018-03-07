#!/usr/bin/env python

""" Creates the DB """

import ConfigParser, sqlite3, os.path

config = ConfigParser.ConfigParser()
config.read("backend.conf")
db_file = config.get("db", "file")

# Needs to be check before sqlite3.connect()
if os.path.isfile(db_file):
    print "DB file: " + db_file + " exists. Exiting"
    exit()

db = sqlite3.connect(db_file)

create_db_string = """
CREATE TABLE "activation" (
    `activation_id` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    `activation_uuid` TEXT NOT NULL UNIQUE,
    `activation_request_date` INTEGER NOT NULL,
    `activation_date` INTEGER,
    `active` INTEGER );

CREATE TABLE "address" (
    `address_id` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    `address_uuid` TEXT NOT NULL UNIQUE,
    `street` TEXT NOT NULL,
    `city` TEXT NOT NULL,
    `state` TEXT NOT NULL,
    `zip` TEXT NOT NULL,
    `country` TEXT NOT NULL );

CREATE TABLE `email` (
    `email_id` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    `email_uuid` TEXT NOT NULL UNIQUE,
    `email` TEXT NOT NULL UNIQUE,
    `confirmed` INTEGER );

CREATE TABLE "phone" (
    `phone_id` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    `phone_uuid` TEXT NOT NULL UNIQUE,
    `phone` TEXT NOT NULL );

CREATE TABLE "ssh_key" (
    `ssh_key_id` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    `ssh_key_uuid` TEXT NOT NULL UNIQUE,
    `pub` TEXT NOT NULL,
    `priv` TEXT NOT NULL );

CREATE TABLE "vpn_key" (
    `vpn_key_id` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    `vpn_key_uuid` TEXT NOT NULL UNIQUE,
    `revoked` INTEGER NOT NULL,
    `srv_blocked` INTEGER NOT NULL,
    `srv_registered` INTEGER NOT NULL,
    `crt` TEXT NOT NULL,
    `key` TEXT NOT NULL );

CREATE TABLE "customer" (
    `customer_id` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    `customer_uuid` TEXT NOT NULL UNIQUE,
    `username` TEXT NOT NULL UNIQUE,
    `password` TEXT NOT NULL,
    `registration_date` INTEGER NOT NULL,
    `last_login` INTEGER,
    `email` TEXT,
    `real_name` TEXT,
    `address_id` INTEGER,
    `phone_id` INTEGER,
    FOREIGN KEY(email) references email(email),
    FOREIGN KEY(address_id) references address(address_id),
    FOREIGN KEY(phone_id) references phone(phone_id) );

CREATE TABLE "server" (
    `server_id` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    `server_uuid` TEXT NOT NULL UNIQUE,
    `customer_id` INTEGER,
    `address_id` INTEGER,
    `activation_uuid` TEXT,
    `ssh_key_id` INTEGER,
    `vpn_key_id` INTEGER,
    FOREIGN KEY(customer_id) references customer(customer_id),
    FOREIGN KEY(address_id) references address(address_id),
    FOREIGN KEY(activation_uuid) references activation(activation_uuid),
    FOREIGN KEY(ssh_key_id) references ssh_key(ssh_key_id),
    FOREIGN KEY(vpn_key_id) references ssh_key(vpn_key_id) );
"""

def main():
    """ good old main """

    c = db.cursor()
    c.executescript(create_db_string)
    db.commit()
    db.close()

    print "DB created"

if __name__ == "__main__":
    main()



