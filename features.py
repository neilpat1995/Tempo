import librosa

class AudioFeatureExtractor(object):
    def __init__(self, audio):
        self._audio = audio
        self._melspec = None

    @property
    def melspectrogram(self):
        if self._melspec is not None:
            return self._melspec

        # Number of mel bands
        n_mels = 128    

        # Window size of STFT
        n_fft = 2048

        # Time frame steps at each fourier 
        # transform, thus each window would
        # be comprised of the end half of
        # the prev window and the start half
        # of the next window
        hop_length = 1024   

        self._melspec = librosa.feature.melspectrogram(
            y = self._audio.y,
            sr = self._audio.sr,
            n_mels = n_mels,
            n_fft = n_fft,
            hop_length = hop_length
        )
        self._melspec = map(list, zip(*self._melspec))
        
        return self._melspec
