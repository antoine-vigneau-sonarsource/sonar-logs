import os
from os import path
import logging

log = logging.getLogger(__name__)

def extract_file_list(input):
    data_items = input.split(',')
    files_list = []
    for item in data_items:
        # Add if it's a file (no check for ce.log validity), if it's a folder add all ce.log files
        if path.isfile(item):
            files_list.append(item)
            log.debug('File to process: {}'.format(item))
        elif path.isdir(item):
            ls_items = os.listdir(item)
            for ls_item in ls_items:
                if ls_item.startswith('ce.'):
                    files_list.append(os.path.join(item, ls_item))
                    log.debug('File to process: {}'.format(os.path.join(item, ls_item)))
    return files_list