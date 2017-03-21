from audio import Audio

import csv
import os

__all__ = [
    'load_songs'
]

BASE_SONG_PATH = os.path.dirname(os.path.abspath(__file__)) + '/songs/'

def load_songs(file_name):
    ret = []
    
    with open(file_name, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if os.path.isfile(BASE_SONG_PATH + row['Song Name']):
                print('adding {}'.format(row['Song Name']))
                try:
                    ret.append(Audio(row).slice(30))
                except:
                    print('{} Failed'.format(row['Song Name']))
                    
    return ret

