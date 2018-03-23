from datetime import datetime
from time import time
from werkzeug.security import generate_password_hash, check_password_hash
from flask import json
from flask_login import UserMixin
from hashlib import md5
import jwt
from uuid import uuid4
from app import app, db, login

followers = db.Table('followers',
        db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
        db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    servers = db.relationship('Server', backref='owner', lazy='dynamic')
    activations = db.relationship('Activation', backref='server', lazy='dynamic')

    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

    followed = db.relationship(
            'User', secondary=followers,
            primaryjoin=(followers.c.follower_id == id),
            secondaryjoin=(followers.c.followed_id == id),
            backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_reset_password_token(self, expires_in=app.config['JWT_PASSWORD_TOKEN_EXPIRES']):
        return jwt.encode(
                {'reset_password': self.id, 'exp': time() + expires_in},
                app.config['SECRET_KEY'],
                algorithm=app.config['JWT_PASSWORD_TOKEN_ALGO']).decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'],
                    algorithms=[app.config['JWT_PASSWORD_TOKEN_ALGO']])['reset_password']
        except:
            return

        return User.query.get(id)

    def get_installation_key_token(self, expires_in=app.config['JWT_INSTALLATION_KEY_EXPIRES']):
        return jwt.encode(
                {'installation_key': self.id, 'exp': time() + expires_in},
                app.config['SECRET_KEY'],
                algorithm=app.config['JWT_PASSWORD_TOKEN_ALGO']).decode('utf-8')

    @staticmethod
    def verify_installation_key_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'],
                    algorithms=[app.config['JWT_PASSWORD_TOKEN_ALGO']])['installation_key']
        except:
            return

        return User.query.get(id)

    def avatar(self,size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(digest, size)

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)
    
    def is_following(self, user):
        return self.followed.filter(
                followers.c.followed_id == user.id).count() > 0

    def followed_posts(self):
        followed = Post.query.join(
                followers, (followers.c.followed_id == Post.user_id)).filter(
                        followers.c.follower_id == self.id)
        own = Post.query.filter_by(user_id = self.id)
        return followed.union(own).order_by(Post.timestamp.desc())

    def get_activations(self):
        return Activation.query.filter_by(user_id = self.id).order_by(Activation.created.desc())

    def get_server_list(self):
        return Server.query.filter_by(user_id = self.id).order_by(Server.created.desc())

    def get_server(self, uuid):
        return Server.query.filter_by(user_id = self.id, uuid = uuid).first()

    def __repr__(self):
        return '<User {}>'.format(self.username)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post {}>'.format(self.body)

class Sshkey(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pub = db.Column(db.String(2048))
    priv = db.Column(db.String(8192))

class Vpnkey(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    crt = db.Column(db.String(8192))
    key = db.Column(db.String(4096))
    revoked = db.Column(db.Boolean, default=False)
    blocked = db.Column(db.Boolean, default=False)

def str_uuid4():
    return str(uuid4().hex)

class Server(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(32), index=True, default=str_uuid4)
    created = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    last_ping = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    servername = db.Column(db.String(32))
    facter_json = db.Column(db.JSON())
    active = db.Column(db.Boolean, default=False)

    sshkey_id = db.Column(db.Integer, db.ForeignKey('sshkey.id'))
    vpnkey_id = db.Column(db.Integer, db.ForeignKey('vpnkey.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class Activation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    active = db.Column(db.Boolean, index=True, default=False)
    last_ping = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    activation_pin = db.Column(db.String(32))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    server_id = db.Column(db.Integer, db.ForeignKey('server.id'))

    def get_server(self):
        return Server.query.filter_by(id=self.server_id).first()


# Facter Stuff

# Need to support more than one MAC / server
facts_mac = db.Table('facter_facts__macaddress',
        db.Column('macaddress_id', db.Integer, db.ForeignKey('facter_macaddress.id')),
        db.Column('facts_id', db.Integer, db.ForeignKey('facter_facts.id'))
)

class FacterVersion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    facterversion = db.Column(db.String(32))

class FacterMacaddress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    macaddress = db.Column(db.String(32))

class FacterArchitecture(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    architecture = db.Column(db.String(32))

class FacterVirtual(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    virtual = db.Column(db.String(128))

class FacterType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(64))

class FacterManufacturer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    manufacturer = db.Column(db.String(64))

class FacterProductname(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    productname = db.Column(db.String(64))

class FacterProcessor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    processor0 = db.Column(db.String(64))

class FacterFacts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    is_virt = db.Column(db.Boolean, index=True, default=False)
    serialnumber = db.Column(db.String(128))
    uuid = db.Column(db.String(128))
    physicalprocessorcount = db.Column(db.Integer)
    processorcount = db.Column(db.Integer)
    memorysize = db.Column(db.String(32))
    memorysize_mb = db.Column(db.String(32))
    blockdevice_sda_size = db.Column(db.String(32))

    facterversion_id = db.Column(db.Integer, db.ForeignKey('facter_version.id'))
    architecture_id = db.Column(db.Integer, db.ForeignKey('facter_architecture.id'))
    virtual_id = db.Column(db.Integer, db.ForeignKey('facter_virtual.id'))
    type_id = db.Column(db.Integer, db.ForeignKey('facter_type.id'))
    manufacturer_id = db.Column(db.Integer, db.ForeignKey('facter_manufacturer.id'))
    productname_id = db.Column(db.Integer, db.ForeignKey('facter_productname.id'))
    processor_id = db.Column(db.Integer, db.ForeignKey('facter_processor.id'))

@login.user_loader
def load_user(id):
    return User.query.get(int(id))
