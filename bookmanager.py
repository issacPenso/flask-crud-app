import os
import time

from flask import Flask, jsonify, json
from flask import render_template
from flask import request
from flask import redirect
from flask import send_from_directory

from flask_sqlalchemy import SQLAlchemy

from azure_storage import AzureStorageImpl
from db_storage import DbStorageImpl
from local_storage import LocalStorageImpl

database_file = 'postgres://drzkyzgd:UbG7pFA7U7wdVQ1B4P5opG8l6J5wU3RH@elmer.db.elephantsql.com:5432/drzkyzgd'


project_dir = os.path.dirname(os.path.abspath(__file__))
# database_file = 'sqlite:///{}'.format(os.path.join(project_dir, 'bookdatabase.db'))

#database_file = 'postgres://postgres:radware@localhost:5432/temp'

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = database_file

db = SQLAlchemy(app)

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
IMAGES = 'images'
LOCAL = 'local'
DB = 'db'
AZURE = 'azure'
STORAGE_TYPE = AZURE

local_storage = LocalStorageImpl()
azure_storage = AzureStorageImpl()


class Books(db.Model):
    title = db.Column(db.String(80), unique=True, nullable=False, primary_key=True)
    img = db.Column(db.LargeBinary, unique=False, nullable=True, primary_key=False)
    last_img_update_timestamp = db.Column(db.String, unique=False, nullable=True, primary_key=False)
    storage_type = db.Column(db.String(80), unique=False, nullable=False, primary_key=False)

    def __repr__(self):
        return '<Title: {}>'.format(self.title)


db_storage = DbStorageImpl(db, Books)


@app.route('/', methods=['GET', 'POST'])
def home():
    books = None
    if request.form:
        try:
            img = request.files.get('img')
            title = request.form.get('title')
            book = Books(title=request.form.get('title'), img=None,
                         last_img_update_timestamp=time.time() if img else None,
                         storage_type=request.form.get('storage_type'))
            db.session.add(book)
            db.session.commit()
            if img:
                if book.storage_type == LOCAL:
                    local_storage.create(book.title, img)
                elif book.storage_type == DB:
                    db_storage.create(book.title, img)
                elif book.storage_type == AZURE:
                    azure_storage.create('%s-%s' % (book.title, book.last_img_update_timestamp), img)
        except Exception as e:
            print('Failed to add book')
            print(e)
    books = Books.query.all()
    return render_template('home.html', books=books, azure_storage=azure_storage)


@app.route('/update', methods=['POST'])
def update():
    try:
        newtitle = request.form.get('newtitle')
        oldtitle = request.form.get('oldtitle')
        book = Books.query.filter_by(title=oldtitle).first()
        img = request.files.get('img')
        previous_img_update_timestamp = '%s' % book.last_img_update_timestamp
        if img:
            book.last_img_update_timestamp = time.time()
        book.title = newtitle
        db.session.commit()
        # UGLY
        if book.storage_type == LOCAL:
            # VERY UGLY
            if img:
                local_storage.update(newtitle, img)
                if newtitle != oldtitle:
                    local_storage.delete(oldtitle)
            else:
                if newtitle != oldtitle:
                    local_storage.rename(oldtitle, newtitle)
        elif book.storage_type == DB:
            if img:
                db_storage.update(book.title, img)
        elif book.storage_type == AZURE:
            # VERY UGLY 2
            old_file_name = '%s-%s' % (oldtitle, previous_img_update_timestamp)
            new_file_name = '%s-%s' % (newtitle, book.last_img_update_timestamp)
            if img:
                azure_storage.update(old_file_name, new_file_name, img)
            else:
                if newtitle != oldtitle:
                    azure_storage.rename(old_file_name, new_file_name)
    except Exception as e:
        print('Couldn\'t update book')
        print(e)
    return redirect('/')


@app.route('/delete', methods=['POST'])
def delete():
    title = request.form.get('title')
    book = Books.query.filter_by(title=title).first()
    db.session.delete(book)
    db.session.commit()
    if book.storage_type == LOCAL:
        local_storage.delete(book.title)
    elif book.storage_type == AZURE:
        blob_name = '%s-%s' % (book.title, book.last_img_update_timestamp)
        azure_storage.delete(blob_name)
    return redirect('/')


@app.route('/images/<book_title>-<last_img_update_timestamp>')
def get_book_image_url(book_title, last_img_update_timestamp=None):
    if last_img_update_timestamp != 'empty':
        book = Books.query.filter_by(title=book_title).first()
        if book.storage_type == LOCAL:
            return local_storage.read(book_title)
        elif book.storage_type == DB:
            if book.img:
                return db_storage.read(book_title)
    else:
        return send_from_directory(IMAGES, 'na-image.png')


@app.route('/api/is-book-title-valid', methods=['GET'])
def is_book_title_valid():
    title = request.args.get('title')
    if not title:
        return jsonify({'status': False, 'reason': 'book title can not be empty or None'})
    else:
        book = Books.query.filter_by(title=title).first()
        if book:
            return jsonify({'status': False, 'reason': 'book with the same title already exist'})
    return jsonify({'status': True, 'reason': ''})


@app.route('/api/test', methods=['GET'])
def test_api():
    return jsonify({'msg': 'test_api'})

@app.route('/api/get-all-books-titles', methods=['GET'])
def get_all_books_titles():
    return Books.query.all('title')

@app.route('/api/search', methods=['GET'])
def search():
    search_term= request.args.get('search_term')
    search_result = Books.query.with_entities(Books.title).filter(Books.title.like('%' + search_term + '%')).all()
    return jsonify({'search_result': [row.title for row in search_result]})

if __name__ == '__main__':
    app.run(debug=True)
