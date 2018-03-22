from flask import render_template, flash, redirect, request, url_for, json, jsonify, Response
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from datetime import datetime, timedelta
from time import time
from random import randrange
from app.models import User, Post, Server, Activation
from app import app, db
from app.email import send_password_reset_email
from app.forms import LoginForm, RegistrationForm, EditProfileForm, PostForm, ActivatePinForm
from app.forms import ResetPasswordRequestForm, ResetPasswordForm, ChangePasswordForm
import logging

HTTP_204_NO_CONTENT = 204

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post is now live')
        return redirect(url_for('index'))

    page = request.args.get('page', 1, type=int)
    posts = current_user.followed_posts().paginate(
            page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('index', page=posts.next_num) \
            if posts.has_next else None
    prev_url = url_for('index', page=posts.prev_num) \
            if posts.has_prev else None

    return render_template('index.html', title='Home Page', form=form,
            posts=posts.items, next_url=next_url, prev_url=prev_url)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))

        login_user(user, remember=form.remember_me.data)

        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')

        return redirect(next_page)

    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = RegistrationForm()

    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))

    return render_template('register.html', title='Register', form=form)

@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(
            page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('user', username=user.username, page=posts.next_num) \
            if posts.has_next else None
    prev_url = url_for('user', username=user.username, page=posts.prev_num) \
            if posts.has_prev else None

    return render_template('user.html', user=user, posts=posts.items,
            next_url=next_url, prev_url=prev_url)

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)

    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me

    return render_template('edit_profile.html', title='Edit Profile', form=form)

@app.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('index'))

    if user == current_user:
        flash('You cannot follow yourself!')
        return redirect(url_for('user', username=username))

    current_user.follow(user)
    db.session.commit()
    flash('You are following {}'.format(username))
    return redirect(url_for('user', username=username))

@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('index'))

    if user == current_user:
        flash('You cannot unfollow yourself!')
        return redirect(url_for('user', username=username))

    current_user.unfollow(user)
    db.session.commit()
    flash('You are not following {}'.format(username))
    return redirect(url_for('user', username=username))

@app.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(
            page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('explore', page=posts.next_num) \
            if posts.has_next else None
    prev_url = url_for('explore', page=posts.prev_num) \
            if posts.has_prev else None

    return render_template('index.html', title='Explore',
        posts=posts.items, next_url=next_url, prev_url=prev_url)

@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Check your email for the instructions to reset your password')
        return redirect(url_for('login'))

    return render_template('reset_password_request.html',
            title='Reset Password', form=form)

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)

@app.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if not current_user.check_password(form.current_password.data):
            flash('Your current password is wrong.')
            return redirect(url_for('change_password'))

        current_user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been changed.')
        return redirect(url_for('edit_profile'))

    return render_template('change_password.html', form=form)

@app.route('/installation_keys')
@login_required
def installation_keys():
    expire_hours = int(app.config['JWT_INSTALLATION_KEY_EXPIRES'] / 3600)
    return render_template('installation_keys.html', title='Installation Keys',
            expire_hours=expire_hours)

@app.route('/download_installation_key')
@login_required
def download_installation_key():
    expires = int(time() + app.config['JWT_INSTALLATION_KEY_EXPIRES'])
    filename = 'iWe-install-key-' + current_user.username + '-' + \
            str(expires) + '.json'
    access_token = {
            'installation_key': current_user.get_installation_key_token(),
            'request_activation_url': url_for('request_activation_pin', _external=True)
            }

    body = 'Downloaded installation key '+ current_user.username + '-' + str(expires)
    post = Post(body=body, author=current_user)
    db.session.add(post)
    db.session.commit()
    flash(body)

    return Response(json.dumps(access_token), mimetype='application/json',
            headers={'Content-Disposition':'attachment;filename=' + filename})

@app.route('/request_activation_pin', methods=['GET', 'POST'])
def request_activation_pin():
    if current_user.is_authenticated:
        return render_template('404.html'), 404

    installation_key = request.headers.get('installation_key')
    if not installation_key:
        return render_template('404.html'), 404

    user = User.verify_installation_key_token(installation_key)
    if not user:
        return render_template('404.html'), 404

    try:
        facter_json = request.get_json()
    except:
        return render_template('404.html'), 404

    try:
        json.dumps(facter_json)
    except:
        return render_template('404.html'), 404
    if not facter_json:
        return render_template('404.html'), 404

    server = Server(owner=user, facter_json=facter_json)
    db.session.add(server)
    db.session.commit()

    activation = Activation(server_id=server.id, user_id=user.id, activation_pin=randrange(1000, 9999))
    db.session.add(activation)
    db.session.commit()

    filename='download_keys_url.json'
    download_keys_url = url_for('download_server_keys', activation_pin=activation.activation_pin, _external=True)
    activate_pin_url = url_for('activate_pin', activation_pin=activation.activation_pin, _external=True)
    activation_pin_json = {'activation_pin':activation.activation_pin,\
                           'download_keys_url': download_keys_url,\
                           'activate_pin_url': activate_pin_url}

    body = 'Activation pin {} requested by {}({}): {}'.format(activation.activation_pin,
            facter_json['manufacturer'], facter_json['productname'], facter_json['serialnumber'])
    post = Post(body=body, author=user)
    db.session.add(post)
    db.session.commit()

    return Response(json.dumps(activation_pin_json),
            mimetype='application/json',
            headers={'Content-Disposition':'attachment;filename=' + filename})

@app.route('/download_server_keys/<activation_pin>')
def download_server_keys(activation_pin):

    if current_user.is_authenticated:
        return render_template('404.html'), 404

    installation_key = request.headers.get('installation_key')
    if not installation_key:
        return render_template('404.html'), 404

    user = User.verify_installation_key_token(installation_key)
    if not user:
        return render_template('404.html'), 404

    activation = Activation.query.filter_by(user_id = user.id, activation_pin = activation_pin).first()
    if activation == None:
        return render_template('404.html'), 404

    activation.last_ping = datetime.utcnow()
    db.session.commit()

    if activation.active == False:
        return '', HTTP_204_NO_CONTENT
    else:
        filename='keys.json'
        keys={'vpn_pvt_key':'super secret private key',\
              'vpn_crt': 'mega master power secret certificate',
              'ssh_pub': 'public key from the biggest known prime number'}
        return Response(json.dumps(keys),
                mimetype='application/json',
                headers={'Content-Disposition':'attachment;filename=' + filename})

def cleanup_activation_pins(user, older_than_hours):
    current_time = datetime.utcnow()
    time_delta = current_time - timedelta(hours=older_than_hours)

    Activation.query.filter(Activation.user_id == user.id, Activation.created < time_delta).delete()
    db.session.commit()

@app.context_processor
def utility_processor():
    def inject_datetime_delta(datetime_obj):

        seconds = (datetime.utcnow() - datetime_obj).total_seconds()

        if seconds < 120:
            minutes_str = 'now'
        else:
            minutes_str = '{} minutes'.format(int(seconds / 60))

        if seconds < 60 * 60:
            hours_str = '1 hour'
        else:
            hours_str = '{} hours'.format(int(seconds / 60 / 60))

        if seconds / 60 <= 60 :
            time_ago_str = minutes_str
        else:
            time_ago_str = hours_str
        return {'time_ago_str': time_ago_str}
    return dict(inject_datetime_delta=inject_datetime_delta)

@app.route('/activation_pins/')
@login_required
def activation_pins():
    
    cleanup_activation_pins(current_user, 48)

    page = request.args.get('page', 1, type=int)

    activations = current_user.get_activations().paginate(
            page, app.config['POSTS_PER_PAGE'], False)

    next_url = url_for('activation_pins', page=activations.next_num) \
            if activations.has_next else None
    prev_url = url_for('activation_pins', page=activations.prev_num) \
            if activations.has_prev else None

    return render_template('list_activation_pins.html', title='List of Activation Pins',
            activations=activations.items, next_url=next_url, prev_url=prev_url)

@app.route('/activate_pin/<activation_pin>', methods=['GET', 'POST'])
@login_required
def activate_pin(activation_pin):
    activation = Activation.query.filter_by(user_id = current_user.id, activation_pin = activation_pin).first()
    if not activation:
        flash('Invalid Pin')
        return redirect(url_for('activation_pins'))

    if activation.active:
        flash('Pin is already active')
        return redirect(url_for('activation_pins'))


    form = ActivatePinForm()
    if form.validate_on_submit():
        if not current_user.check_password(form.password.data):
            print ('wrong pw')
            flash('Wrong password.')
            return redirect(url_for('activate_pin',activation_pin=activation_pin))

        activation.active = True
        db.session.commit()
        flash('Pin {} is now active'.format(activation_pin))

        body = 'Pin {} activated'.format(activation.activation_pin)
        post = Post(body=body, author=current_user)
        db.session.add(post)
        db.session.commit()

        return redirect(url_for('activation_pins'))

    elif request.method == 'GET':
        form.pin.data = activation_pin
        return render_template('activate_pin.html', title='Activate Your Server', form=form)
    else:
        flash('Password or pin invalid.')
        return redirect(url_for('activate_pin', activation_pin=activation_pin))
