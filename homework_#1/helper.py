import argparse
import sys
from boto import BotoHelper


class CloudPhoto:

    def __init__(self):
        self.boto_helper = BotoHelper()
        parser = argparse.ArgumentParser(
            description='Cloudphoto',
            usage='''cloudphoto <command> [<args>]

The most commonly used cloudphoto commands are:
   upload     Upload photo to yandex storage
   download   Download photo from yandex storage
   list       List of albums
''')
        parser.add_argument('command', help='Subcommand to run')
        args = parser.parse_args(sys.argv[1:2])
        if not hasattr(self, args.command):
            print('Unrecognized command')
            parser.print_help()
            exit(1)
        getattr(self, args.command)()

    def upload(self):
        parser = argparse.ArgumentParser(
            description='Upload photo to yandex storage')
        parser.add_argument('-p', help='File path', required=True)
        parser.add_argument('-a', help='Album name', required=True)
        args = parser.parse_args(sys.argv[2:])
        print(self.boto_helper.upload_photos_to_album(args.p, args.a))

    def download(self):
        parser = argparse.ArgumentParser(
            description='Download photo from yandex storage')
        parser.add_argument('-p', help='File path', required=True)
        parser.add_argument('-a', help='Album name', required=True)
        args = parser.parse_args(sys.argv[2:])
        print(self.boto_helper.download_photos_to_path(args.p, args.a))

    def list(self):
        parser = argparse.ArgumentParser(
            description='Get list of albums from yandex storage')
        parser.add_argument('-a', help='Album name')
        args = parser.parse_args(sys.argv[2:])
        self.boto_helper.get_console_albums(args.a)


if __name__ == '__main__':
    CloudPhoto()
