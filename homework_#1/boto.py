import configparser

import boto3
import glob
import os
from pathlib import Path


def get_config_variables(filename):
    config = configparser.ConfigParser()
    config.read(filename)
    return config


file_suffix = (".jpg", ".jpeg")


class BotoHelper:

    def __init__(self):
        self.session = boto3.session.Session()
        self.s3 = self.session.client(
            service_name='s3',
            endpoint_url='https://storage.yandexcloud.net'
        )

        self.config = get_config_variables("keys.ini")
        self.bucket_name = self.config['yandex']['bucket_name']
        self.album_postfix = '/'

    def get_objects(self):
        return self.s3.list_objects(Bucket=self.bucket_name)['Contents']

    def create_album(self, album_name: str):
        self.s3.put_object(Bucket=self.bucket_name, Key=f'{album_name}/', StorageClass='STANDARD')

    @staticmethod
    def check_path_or_raise_error(path: str):
        path_dir = Path(path)
        if not path_dir.is_dir():
            raise FileNotFoundError("Path does not exist")

    def get_photos_from_folder(self, path: str):
        self.check_path_or_raise_error(path)
        return glob.glob(f'{path}{os.sep}*[{file_suffix[0]}|{file_suffix[1]}]')

    def upload_single_file(self, path: str, name: str):
        self.s3.upload_file(path, self.bucket_name, name)

    def upload_photos_list(self, photos_list: list, album: str):
        for photo in photos_list:
            name = photo.split('\\')[-1]
            self.upload_single_file(photo, f'{album}/{name}')

    def upload_photos_to_album(self, path: str, album: str):
        try:
            photos = self.get_photos_from_folder(path)
            if album is not None:
                albums = self.get_console_albums(album, print_albums=False)
                albums = list(map(lambda x: x['Key'], albums))
                if album + self.album_postfix in albums:
                    # upload file
                    self.upload_photos_list(photos, album)
                    return f"Uploaded {len(photos)} photos"
                else:
                    # create album and upload file
                    self.create_album(album)
                    self.upload_photos_list(photos, album)
                    return f"Created '{album}' album\n" \
                           f"Uploaded {len(photos)} photos"
        except FileNotFoundError as ex:
            return ex

    def _download_photos_from_album(self, albums: list, path: str):
        photos = list(filter(lambda x: (x.endswith(file_suffix[0]) or x.endswith(file_suffix[1])), albums))
        for photo in photos:
            name = photo.split('/')[-1]
            file_path = os.path.join(path, name)
            file = open(file_path, 'wb')
            get_object_response = self.s3.get_object(Bucket=self.bucket_name, Key=photo)
            file.write(get_object_response['Body'].read())
            file.close()

    def download_photos_to_path(self, path: str, album: str):
        try:
            self.check_path_or_raise_error(path)
            if album is not None:
                albums = self.get_console_albums(album, print_albums=False)
                albums = list(map(lambda x: x['Key'], albums))
                if album + self.album_postfix in albums:
                    self._download_photos_from_album(albums, path)
                else:
                    return f"Cant find album name: '{album}'" \
                           f"{albums}"
        except FileNotFoundError:
            return "Cant find path"

    @staticmethod
    def print_objects(objects: list):
        if len(objects) == 0:
            print("No albums")
        for album in range(len(objects)):
            print(objects[album]['Key'])

    def get_console_albums(self, album_name: str = None, print_albums: bool = True):
        albums = self.get_objects()
        if album_name is None:
            albums_arr = list(filter(lambda x: x['Size'] == 0, self.get_objects()))
            if print_albums:
                self.print_objects(albums_arr)
        else:
            albums_arr = list(filter(lambda x: x['Key'].startswith(f'{album_name}{self.album_postfix}'), albums))
            if print_albums:
                self.print_objects(albums_arr)
        return albums_arr


boto = BotoHelper()
boto.get_console_albums()