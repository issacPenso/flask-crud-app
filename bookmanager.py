import os
from io import BytesIO

from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import send_file
from flask import url_for
from sqlalchemy_imageattach.context import store_context
# from werkzeug.utils import secure_filename

from flask_sqlalchemy import SQLAlchemy

UPLOAD_FOLDER = '/path/to/the/uploads'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

# database_file = 'postgres://drzkyzgd:UbG7pFA7U7wdVQ1B4P5opG8l6J5wU3RH@elmer.db.elephantsql.com:5432/drzkyzgd'


project_dir = os.path.dirname(os.path.abspath(__file__))
database_file = 'sqlite:///{}'.format(os.path.join(project_dir, 'bookdatabase.db'))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = database_file
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db = SQLAlchemy(app)


class Books(db.Model):
    title = db.Column(db.String(80), unique=True, nullable=False, primary_key=True)
    img = db.Column(db.LargeBinary, unique=False, nullable=True, primary_key=False)

    def __repr__(self):
        return '<Title: {}>'.format(self.title)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
def home():
    books = None
    if request.form:
        try:
            img = request.files['img']
            book = Books(title=request.form.get('title'), img=img.read())
            db.session.add(book)
            db.session.commit()
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
        img = request.files['img']
        book.img = img.read()
        book.title = newtitle
        db.session.commit()
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
    return redirect('/')


@app.route('/images/<book_title>')
def get_book_image_url(book_title):
    book = Books.query.filter_by(title=book_title).first()
    return send_file(BytesIO(book.img), attachment_filename=book.title, as_attachment=False)


if __name__ == '__main__':
    app.run(debug=True)
