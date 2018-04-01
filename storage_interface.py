import abc


class StorageInterface(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def create(self, book_title, img_file):
        return

    @abc.abstractmethod
    def read(self, book_title):
        return

    @abc.abstractmethod
    def update(self, book_title, img_file):
        return

    @abc.abstractmethod
    def delete(self, book_title):
        return
