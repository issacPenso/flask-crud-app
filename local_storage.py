import os
from flask import send_from_directory

from storage_interface import StorageInterface

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
IMAGES = 'images'
TARGET = os.path.join(APP_ROOT, '%s/' % IMAGES)

class LocalStorageImpl(StorageInterface):
    def create(self, book_title, img_file):
        if not os.path.isdir(TARGET):
            os.mkdir(TARGET)
        destination = "/".join([TARGET, book_title])
        img_file.save(destination)
        img_file.close

    def read(self, book_title):
        return send_from_directory(IMAGES, book_title)

    def update(self, book_title, img_file):
        if img_file:
            if not os.path.isdir(TARGET):
                os.mkdir(TARGET)
            destination = "/".join([TARGET, book_title])
            img_file.save(destination)

    def rename(self, old_title, new_title):
        source = "/".join([TARGET, old_title])
        destination = "/".join([TARGET, new_title])
        if os.path.exists(source):
            os.rename(source, destination)

    def delete(self, book_title):
        destination = '%s/%s' % (IMAGES, book_title)
        if os.path.exists(destination):
            return os.remove(destination)
