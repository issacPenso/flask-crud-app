from flask import send_file

from storage_interface import StorageInterface
from io import BytesIO


class DbStorageImpl(StorageInterface):
    def __init__(self, db, table):
        self.db = db
        self.table = table

    def create(self, book_title, img_file):
        book = self.table.query.filter_by(title=book_title).first()
        book.img = img_file.read()
        self.db.session.commit()

    def read(self, book_title):
        book = self.table.query.filter_by(title=book_title).first()
        if book.img:
            return send_file(BytesIO(book.img), attachment_filename=book.title, as_attachment=False)
        else:
            return None

    def update(self, book_title, img_file):
        book = self.table.query.filter_by(title=book_title).first()
        if img_file:
            book.img = img_file.read()
            self.db.session.commit()

    def delete(self, book_title):
        book = self.table.query.filter_by(title=book_title).first()
        book.img = None
        self.db.session.commit()
