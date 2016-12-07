import os
import sys
import hashlib
import logging
import argparse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

parser = argparse.ArgumentParser()
group = parser.add_mutually_exclusive_group()
parser.add_argument("dirpaths", nargs='+', help="detect duplicate files in a given number of directories")
group.add_argument("-d", "--delete",
                   action='store_true',
                   help='delete flag, delete all duplicate files')
group.add_argument("-l", "--list",
                   action='store_true',
                   help='list files flag, list all duplicate files')
args = parser.parse_args()


def read_in_chunks(fileobj, chunk_size=1024):
    # Generator function that reads a file in chunks of bytes
    while True:
        chunk = fileobj.read(chunk_size)
        if not chunk:
            return
        yield chunk


def find_duplicate_sizes(path_roots):
    """
    This is a pre-scanning function.  It will eliminate unnecessary hashing by considering uniquely sized
    files as unique files.
    :param path_roots: One or more directories you want scanned for duplicates, passed in as parameters to the script
    :return: a dict of files with a non unique file sizes to be hashed for duplicate detecting
    """

    logger.info('Finding duplicate sizes within the given directories')
    unique_sizes = {}
    duplicate_sizes = {}  # returned, key is full path of file with value as file size
    remove_from_unique = []

    for a_path in path_roots:
        logger.info('In {} top directory'.format(a_path))
        for dir_path, subdirs, files in os.walk(a_path):
            logger.info('Looking in {} directory'.format(dir_path))
            for file_name in files:
                full_path = os.path.join(dir_path, file_name)
                file_size = os.stat(full_path).st_size
                if file_size in unique_sizes:
                    # if file size exists it is not unique, so add it to the duplicate dict, and
                    # mark for removal from unique file size dict
                    remove_from_unique.append(file_size)  # added but wont remove from unique list until done checking
                    duplicate_sizes[full_path] = file_size
                else:
                    # dictionary item where key is a file size and value is the full file path
                    unique_sizes[file_size] = full_path
    for dupes in set(remove_from_unique):
        # removal files that no longer have unique sizes from the unique_sizes dict
        duplicate_sizes[unique_sizes.pop(dupes)] = dupes
    logger.debug('There are {} files with duplicate sizes'.format(len(duplicate_sizes)))
    logger.debug('There are {} files that have unique sizes'.format(len(unique_sizes)))
    return duplicate_sizes


def find_duplicate_files(file_dict, hash=hashlib.sha1):
    """
    This will create a dict of all duplicate files.  Only dupes are in this dict so if 2 of the same file exist,
    one will be in the dict.  If 3 of the same file exist, 2 will be in the dict.
    :param file_dict: dictionary of key:path value: size
    :param hash: hashing algorithm with default sha1
    :return: a dict with key: path, value: [hash, size] of duplicate files
    """
    unique_hashes = {}  # these are the unique files,
    duplicate_files = {}  # these are duplicate files, that will be returned in a dictionary
    dupe_count = 0
    unique_count = 0
    for file_path in file_dict:
        hashobj = hash()
        for chunk in read_in_chunks(open(file_path, 'rb')):
            hashobj.update(chunk)
        fhash_fsize = (hashobj.digest(), os.stat(file_path).st_size)
        duplicate = unique_hashes.get(fhash_fsize, None)
        if duplicate:
            dupe_count += 1
            duplicate_files[file_path] = fhash_fsize
            logger.info('{} is a duplicate of {}'.format(file_path, unique_hashes[fhash_fsize]))
        else:
            unique_count += 1
            unique_hashes[fhash_fsize] = file_path
    logger.info('Same size file dupe count: %d', dupe_count)
    logger.info('Same size unique count: %d', unique_count)
    return duplicate_files


def delete_duplicates(file_dict):
    """
    Delete all duplicate files.
    :param file_dict: a dictionary of duplicate files with key: path, value: [hash, size]
    """
    logger.info('Deleting duplicate files now')
    dupe_count = 0
    for file in file_dict:
        print 'deleting: ' + str(file)
        os.remove(str(file))
        dupe_count += 1
    print 'a total of ' + str(dupe_count) + ' files were deleted'


def print_duplicate_files(file_dict):
    """
    List all duplicate files.
    :param file_dict: a dictionary of duplicate files with key: path, value: [hash, size]
    """
    dupe_count = 0
    for file in file_dict:
        print 'size: ' + str(file_dict[file][1]) + ' - ' + 'path: ' + str(file)
        dupe_count += 1
    print 'dupe count: ' + str(dupe_count)


dupe_sizes = find_duplicate_sizes(args.dirpaths[0:])
dupes = find_duplicate_files(dupe_sizes)
if args.delete:
    delete_duplicates(dupes)
if args.list:
    print_duplicate_files(dupes)
