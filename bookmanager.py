import os
import time

from flask import Flask
from flask import render_template
from flask import request
from flask import redirect


from flask_sqlalchemy import SQLAlchemy

from db_storage import DbStorageImpl
from local_storage import LocalStorageImpl

# database_file = 'postgres://drzkyzgd:UbG7pFA7U7wdVQ1B4P5opG8l6J5wU3RH@elmer.db.elephantsql.com:5432/drzkyzgd'


project_dir = os.path.dirname(os.path.abspath(__file__))
database_file = 'sqlite:///{}'.format(os.path.join(project_dir, 'bookdatabase.db'))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = database_file

db = SQLAlchemy(app)

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
IMAGES = 'images'
LOCAL = 'local'
DB = 'db'
CLOUD = 'cloud'
STORAGE_TYPE = LOCAL

local_storage = LocalStorageImpl()


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
            last_img_update_timestamp = time.time()
            book = Books(title=request.form.get('title'), img=None,
                         last_img_update_timestamp=last_img_update_timestamp,
                         storage_type=request.form.get('storage_type'))
            db.session.add(book)
            db.session.commit()
            if img:
                if book.storage_type == LOCAL:
                    local_storage.create(book.title,img)
                elif book.storage_type == DB:
                    db_storage.create(book.title, img)
                elif book.storage_type == CLOUD:
                    pass
        except Exception as e:
            print('Failed to add book')
            print(e)
    books = Books.query.all()
    return render_template('home.html', books=books)


@app.route('/update', methods=['POST'])
def update():
    try:
        newtitle = request.form.get('newtitle')
        oldtitle = request.form.get('oldtitle')
        book = Books.query.filter_by(title=oldtitle).first()
        img = request.files.get('img')
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
        elif book.storage_type == CLOUD:
            pass
    except Exception as e:
        print('Couldn\'t update book title')
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
    elif book.storage_type == CLOUD:
        pass
    return redirect('/')


@app.route('/images/<book_title>-<last_img_update_timestamp>')
def get_book_image_url(book_title, last_img_update_timestamp):
    book = Books.query.filter_by(title=book_title).first()
    if book.storage_type == LOCAL:
        return local_storage.read(book_title)
    elif book.storage_type == DB:
        if book.img:
            return db_storage.read(book_title)
    elif book.storage_type == CLOUD:
        return

if __name__ == '__main__':
    app.run(debug=True)
