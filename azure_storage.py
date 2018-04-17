from azure.storage.blob import BlockBlobService
from azure.storage.file import ContentSettings
from azure.common import AzureMissingResourceHttpError

from storage_interface import StorageInterface

account_key = 'JDPO4nWnfcanDfiQADLABhFibMK5VXfLFM6XoPTQX7MxWD6pG5KXeXBJ0m7Ki/lJVa24iAfUPRrtcKbahyTnnw=='
account_name = 'izik1'
sas_token = '?sv=2017-07-29&ss=bf&srt=sco&sp=r&se=2018-04-30T21:00:00Z&st=2018-04-01T21:00:00Z&spr=https&sig=vpwGkoD46mqBTN4A6Lq%2FN3d7Dfk%2FaZ4T7Dye3y8qKv4%3D'

block_blob_service = BlockBlobService(account_name=account_name, account_key=account_key)

MY_CONTAINER = 'flaskcrudapp'


class AzureStorageImpl(StorageInterface):
    def create(self, file_name, img_file):
        block_blob_service.create_container(MY_CONTAINER)
        block_blob_service.create_blob_from_bytes(MY_CONTAINER, file_name, img_file.read(),
                                                  content_settings=ContentSettings(content_type='image/png'))

    def read(self, file_name):
        blob_url = block_blob_service.make_blob_url(MY_CONTAINER, file_name)
        return '%s%s' % (blob_url, sas_token)

    def update(self, old_file_name, new_file_name, img_file):
        block_blob_service.create_blob_from_bytes(MY_CONTAINER, new_file_name, img_file.read(),
                                                  content_settings=ContentSettings(content_type='image/png'))
        if old_file_name != new_file_name:
            self.delete(old_file_name)

    def rename(self, old_file_name, new_file_name):
        block_blob_service.copy_blob(MY_CONTAINER, new_file_name, block_blob_service.make_blob_url(MY_CONTAINER, old_file_name))
        if old_file_name != new_file_name:
            self.delete(old_file_name)

    def delete(self, file_name):
        blob_props = None
        try:
            blob_props = block_blob_service.get_blob_properties(MY_CONTAINER, file_name)
        except AzureMissingResourceHttpError:
            pass
        if blob_props:
            block_blob_service.delete_blob(MY_CONTAINER, file_name)
