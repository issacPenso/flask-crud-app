import abc


class storageInterface(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def upload(self, file, filename):
        return

    @abc.abstractmethod
    def read(self, filename):
        return

    @abc.abstractmethod
    def update(self, file, filename):
        return

    @abc.abstractmethod
    def getUrl(self):
        return

