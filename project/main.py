# Modules updated for task 7 and 9 - Harris Barker and Alex He
from flask import Blueprint, render_template, request, flash, redirect, url_for, send_from_directory, current_app, session, Flask, request, jsonify, g
from .models import Photo, User, Comment
from sqlalchemy import asc, text
from . import db
import os

main = Blueprint('main', __name__)

# Home page call rendering, fetching all images, added for task 7 - Harris Barker
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
                         keywords=request.form['keywords'],
                         file=file.filename)
        db.session.add(newPhoto)
        flash('New Photo %s Successfully Created' % newPhoto.name)
        db.session.commit()
        return redirect(url_for('main.homepage'))
    else:
        return render_template('upload.html')

@main.route('/photo/<int:photo_id>/edit/', methods=['GET', 'POST'])
@login_required
def editPhoto(photo_id): # Updated for task 7 - Harris Barker
    editedPhoto = db.session.query(Photo).filter_by(id=photo_id).one()
    if session['username'] != editedPhoto.name and session['role'] != 'admin':
        flash('You do not have permission to edit this photo.', 'danger')
        return redirect(url_for('main.homepage'))

    if request.method == 'POST': # Added for task 7 - Harris Barker
        if request.form['user']:
            editedPhoto.name = request.form['user']
            editedPhoto.caption = request.form['caption']
            editedPhoto.description = request.form['description']
            editedPhoto.keywords = request.form['keywords']
            db.session.add(editedPhoto)
            db.session.commit()
            flash('Photo Successfully Edited %s' % editedPhoto.name)
            return redirect(url_for('main.homepage'))
    else:
        return render_template('edit.html', photo=editedPhoto)

@main.route('/photo/<int:photo_id>/delete/', methods=['GET', 'POST'])
@login_required
def deletePhoto(photo_id): # Updated for task 7 - Harris Barker
    fileResults = db.session.execute(text('select file from photo where id = ' + str(photo_id)))
    filename = fileResults.first()[0]
    filepath = os.path.join(current_app.config["UPLOAD_DIR"], filename)
    os.unlink(filepath)
    db.session.execute(text('delete from photo where id = ' + str(photo_id)))
    db.session.commit()

    flash('Photo id %s Successfully Deleted' % photo_id)
    return redirect(url_for('main.homepage'))


@main.route('/photo/<int:photo_id>', methods = ['GET'])
def photo_page(photo_id):
    photo = db.session.query(Photo).get(photo_id)
    if not photo:
        flash('Photo not found.', 'error')
        return redirect(url_for('main.homepage'))
    return render_template('photo_page.html', photo=photo)

#Task 9 - Alex
@main.route('/photo/<int:photo_id>/comments', methods=['POST'])
@login_required
def add_comment(photo_id):
    data = request.get_json()
    comment_text = data.get('comment_text')
    user_id = session['user_id']

    # Using parameterized query to prevent SQL injection    SQLAlchemy text function specifies placeholders for values to be inserted
    stmt = text("INSERT INTO comment (photo_id, user_id, comment_text) VALUES (:photo_id, :user_id, :comment_text)")
    db.session.execute(stmt, {"photo_id": photo_id, "user_id": user_id, "comment_text": comment_text})
    db.session.commit()
    return jsonify({'message': 'Comment added successfully'}), 201

#Task 9 - Alex
@main.route('/search', methods=['GET'])
def search_photos():
    keyword = request.args.get('keyword')

       # Using SQLAlchemy's parameterized queries to prevent SQL injection
    photos = Photo.query.filter(Photo.metadata.contains(keyword)).all()

    return jsonify([{
        'id': photo.id,
        'url': photo.url,
        'metadata': photo.metadata
    } for photo in photos])

if __name__ == '__main__':
    main.run(debug=True)