from flask import Blueprint, render_template, request, flash, redirect, url_for, send_from_directory, current_app, session
from .models import Photo, User
from sqlalchemy import asc, text
from . import db
import os

main = Blueprint('main', __name__)

def login_required(f):
    def wrap(*args, **kwargs):
        if 'user_id' not in session:
            flash('You need to be logged in to view this page.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    wrap.__name__ = f.__name__
    return wrap

def admin_required(f):
    def wrap(*args, **kwargs):
        if session.get('role') != 'admin':
            flash('You need to be an admin to view this page.', 'danger')
            return redirect(url_for('main.homepage'))
        return f(*args, **kwargs)
    wrap.__name__ = f.__name__
    return wrap

@main.route('/')
def homepage():
    photos = db.session.query(Photo).order_by(asc(Photo.file))
    return render_template('index.html', photos=photos)

@main.route('/uploads/<name>')
def display_file(name):
    return send_from_directory(current_app.config["UPLOAD_DIR"], name)

@main.route('/upload/', methods=['GET', 'POST'])
@login_required
def newPhoto():
    if request.method == 'POST':
        file = None
        if "fileToUpload" in request.files:
            file = request.files.get("fileToUpload")
        else:
            flash("Invalid request!", "error")

        if not file or not file.filename:
            flash("No file selected!", "error")
            return redirect(request.url)

        filepath = os.path.join(current_app.config["UPLOAD_DIR"], file.filename)
        file.save(filepath)

        newPhoto = Photo(name=session['username'],
                         caption=request.form['caption'],
                         description=request.form['description'],
                         file=file.filename)
        db.session.add(newPhoto)
        flash('New Photo %s Successfully Created' % newPhoto.name)
        db.session.commit()
        return redirect(url_for('main.homepage'))
    else:
        return render_template('upload.html')

@main.route('/photo/<int:photo_id>/edit/', methods=['GET', 'POST'])
@login_required
def editPhoto(photo_id):
    editedPhoto = db.session.query(Photo).filter_by(id=photo_id).one()
    if session['username'] != editedPhoto.name and session['role'] != 'admin':
        flash('You do not have permission to edit this photo.', 'danger')
        return redirect(url_for('main.homepage'))

    if request.method == 'POST':
        if request.form['user']:
            editedPhoto.name = request.form['user']
            editedPhoto.caption = request.form['caption']
            editedPhoto.description = request.form['description']
            db.session.add(editedPhoto)
            db.session.commit()
            flash('Photo Successfully Edited %s' % editedPhoto.name)
            return redirect(url_for('main.homepage'))
    else:
        return render_template('edit.html', photo=editedPhoto)

@main.route('/photo/<int:photo_id>/delete/', methods=['GET', 'POST'])
@login_required
def deletePhoto(photo_id):
    fileResults = db.session.execute(text('select file from photo where id = ' + str(photo_id)))
    filename = fileResults.first()[0]
    filepath = os.path.join(current_app.config["UPLOAD_DIR"], filename)
    os.unlink(filepath)
    db.session.execute(text('delete from photo where id = ' + str(photo_id)))
    db.session.commit()

    flash('Photo id %s Successfully Deleted' % photo_id)
    return redirect(url_for('main.homepage'))
