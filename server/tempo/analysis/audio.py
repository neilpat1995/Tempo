from tempo.analysis.features import AudioFeatureExtractor

import librosa
import os

class Audio(object):
    SAMPLING_RATE = 22050   # Use the same sampling rate on all 
                            # audio files - 22.050 kHz

    def __init__(self, file_path, y = None, sr = None):
        if y is not None and sr is not None:
            self.y = y
            self.sr = sr
        elif file_path is not None:
            self.file_path = file_path

            y, sr = librosa.load(file_path, sr = Audio.SAMPLING_RATE)
            self.y = y
            self.sr = sr
        else:
            print("[Warning] - Empty audio object initialized")

        self.features = AudioFeatureExtractor(self)

    def slice(self, interval, mid = None):
        if mid is None:
            mid = len(self.y) / 2
        else:
            mid *= self.sr

        # convert time interval to frequency interval
        # based on the sampling rate
        interval = self.sr * interval

        step = interval / 2
        s = int(mid - step)
        e = int(mid + step)

        return Audio(self.file_path, y = self.y[s:e], sr = self.sr)

    '''
    @property
    def song_name(self):
        return self._properties['Song Name']

    @property
    def weather(self):
        return self._properties['Weather'].lower()

    @property
    def activity(self):
        return self._properties['Activity'].lower()

    @property
    def mood(self):
        return self._properties['Mood'].lower()
    '''

    @property
    def duration(self):
        return float(len(self.y) / self.sr)
