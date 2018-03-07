"""
Flask app for testing the OpenID Connect extension.
"""
from flask import Flask
from flask_oidc import OpenIDConnect

def index():
    return "too many secrets", 200, {
        'Content-Type': 'text/plain; charset=utf-8'
    }

def create_app(config, oidc_overrides=None):
    app = Flask(__name__)
    app.config.update(config)
    if oidc_overrides is None:
        oidc_overrides = {}
    oidc = OpenIDConnect(app, **oidc_overrides)
    app.route('/')(oidc.check(index))
    return app

if __name__ == '__main__':
    APP = create_app({
        'OIDC_CLIENT_SECRETS': './client_secrets.json',
        'OIDC_ID_TOKEN_COOKIE_SECURE': False,
        'SECRET_KEY': 'secret'})
    APP.run(host="127.0.0.1", port=8080, debug=True)
