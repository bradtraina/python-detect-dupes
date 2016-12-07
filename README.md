# detect-dupes.py

this script detects duplicates in the given folder(s) and allows user to list or delete files

usage: detect-dupes.py [-h] [-d | -l] dirpaths [dirpaths ...]

positional arguments:
  dirpaths      detect duplicate files in a given number of directories

optional arguments:
  -h, --help    show this help message and exit
  -d, --delete  delete flag, delete all duplicate files
  -l, --list    list files flag, list all duplicate files
