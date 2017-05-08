import fnmatch
import os
import zipfile

import sys


def unzip(path_to_zip_file, directory_to_extract_to):
    zip_ref = zipfile.ZipFile(path_to_zip_file, 'r')
    zip_ref.extractall(directory_to_extract_to)
    zip_ref.close()

def unzip_in_dir(root_dir):
    pattern = '*.zip'
    for root, dirs, files in os.walk(root_dir):
        for filename in fnmatch.filter(files, pattern):
            print(os.path.join(root, filename))
            zipfile.ZipFile(os.path.join(root, filename)).extractall(os.path.join(root, os.path.splitext(filename)[0]))

if __name__ == '__main__':
    if len(sys.argv) < 2:
        raise Exception('root_dir not passed')
    root_dir = sys.argv[1]
    print('unzip all files in {0}.'.format(root_dir))
    unzip_in_dir(root_dir)
