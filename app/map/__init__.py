import csv
import json
import logging
import os

from flask import Blueprint, render_template, abort, url_for, current_app, jsonify
from flask_login import current_user, login_required
from jinja2 import TemplateNotFound

from app.db import db
from app.db.models import Location
from app.songs.forms import csv_upload
from werkzeug.utils import secure_filename, redirect
from flask import Response

map = Blueprint('map', __name__,
                        template_folder='templates')

@map.route('/locations', methods=['GET'], defaults={"page": 1})
@map.route('/locations/<int:page>', methods=['GET'])
def browse_locations(page):
    page = page
    per_page = 10
    pagination = Location.query.paginate(page, per_page, error_out=False)
    data = pagination.items
    try:
        return render_template('browse_locations.html',data=data,pagination=pagination)
    except TemplateNotFound:
        abort(404)

@map.route('/locations_datatables/', methods=['GET'])
def browse_locations_datatables():

    data = Location.query.all()

    try:
        return render_template('browse_locations_datatables.html',data=data)
    except TemplateNotFound:
        abort(404)

@map.route('/api/locations/', methods=['GET'])
def api_locations():
    data = Location.query.all()
    try:
        return jsonify(data=[location.serialize() for location in data])
    except TemplateNotFound:
        abort(404)


@map.route('/locations/map', methods=['GET'])
def map_locations():
    google_api_key = current_app.config.get('GOOGLE_API_KEY')
    log = logging.getLogger("myApp")
    log.info(google_api_key)
    try:
        return render_template('map_locations.html',google_api_key=google_api_key)
    except TemplateNotFound:
        abort(404)



@map.route('/locations/upload', methods=['POST', 'GET'])
@login_required
def location_upload():
    form = csv_upload()
    if form.validate_on_submit():
        filename = secure_filename(form.file.data.filename)
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        form.file.data.save(filepath)
        list_of_locations = []
        with open(filepath) as file:
            csv_file = csv.DictReader(file)
            for row in csv_file:
                list_of_locations.append(Location(row['location'],row['longitude'],row['latitude'],row['population']))

        current_user.locations = list_of_locations
        db.session.commit()

        return redirect(url_for('map.browse_locations'))

    try:
        return render_template('upload_locations.html', form=form)
    except TemplateNotFound:
        abort(404)

# start of new code

@auth.route('/locations')
@login_required
@admin_required
def browse_users():
    data = User.query.all()
    titles = [('email', 'Email'), ('registered_on', 'Registered On')]
    retrieve_url = ('auth.retrieve_user', [('user_id', ':id')])
    edit_url = ('auth.edit_user', [('user_id', ':id')])
    add_url = url_for('auth.add_user')
    delete_url = ('auth.delete_user', [('user_id', ':id')])

    current_app.logger.info("Browse page loading")

    return render_template('browse.html', titles=titles, add_url=add_url, edit_url=edit_url, delete_url=delete_url,
                           retrieve_url=retrieve_url, data=data, User=User, record_type="Users")


@auth.route('/locations/<int:location_id>')
@login_required
def retrieve_user(user_id):
    user = User.query.get(user_id)
    return render_template('profile_view.html', user=user)


@auth.route('/users/<int:user_id>/edit', methods=['POST', 'GET'])
@login_required
def edit_locations(location_id):
    location = Location.query.get(location_id)
    form = user_edit_form(obj=user)
    if form.validate_on_submit():
        user.about = form.about.data
        user.is_admin = int(form.is_admin.data)
        db.session.add(user)
        db.session.commit()
        flash('Location Edited Successfully', 'success')
        current_app.logger.info("edited a location")
        return redirect(url_for('auth.browse_locations'))
    return render_template('user_edit.html', form=form)


@auth.route('/users/new', methods=['POST', 'GET'])
@login_required
def add_user():
    form = register_form()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            user = User(email=form.email.data, password=generate_password_hash(form.password.data))
            db.session.add(user)
            db.session.commit()
            flash('Congratulations, you just created a user', 'success')
            return redirect(url_for('auth.browse_users'))
        else:
            flash('Already Registered')
            return redirect(url_for('auth.browse_users'))
    return render_template('user_new.html', form=form)


@auth.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
def delete_user(user_id):
    location = User.query.get(user_id)
    if user.id == current_user.id:
        flash("You can't delete yourself!")
        return redirect(url_for('auth.browse_users'), 302)
    db.session.delete(user)
    db.session.commit()
    flash('User Deleted', 'success')
    return redirect(url_for('auth.browse_users'), 302)
