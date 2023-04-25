from collections import defaultdict
from pathlib import Path
import numpy as np
import scipy.io as sio


PATH = Path('./data/recorded')
FS = 25000
ORIG_SAMPLE_LEN = 1024
NEW_SAMPLE_LEN = 2048
LEN_AUDIO = (1499 // (NEW_SAMPLE_LEN // ORIG_SAMPLE_LEN)) * NEW_SAMPLE_LEN


def load():
    DS2_2 = defaultdict(lambda: np.array([]))
    DS2_1 = defaultdict(lambda: np.array([]))

    for filename in PATH.iterdir():
        if filename.is_file() and filename.suffix == '.wav':
            p, speed, load_val, *other = filename.stem.split('_')
            fs, data = sio.wavfile.read(filename)
            if data.dtype == np.float64 and fs == FS:
                clsname = '_'.join([p, speed, load_val])
                if '2' in other:
                    d = DS2_2
                else:
                    d = DS2_1
                d[clsname] = np.append(d[clsname], data[:LEN_AUDIO])
            else:
                print(f'inappropriate format: {data.dtype.name} {fs=} {filename}')
                # if fs > 25000:
                #     if data.dtype == np.int16:
                #         data = data / (2**15-1)
                #     data = librosa.resample(data, orig_sr=fs, target_sr=DS2_FS)
                #     sio.wavfile.write(DS2_PATH / (filename.stem + '_25kHz' + filename.suffix),
                #                       DS2_FS, data)

    CLASSES = sorted(DS2_2.keys())
    data_2 = np.empty((len(CLASSES), *list(DS2_2.values())[0].shape))
    for i, cls in enumerate(CLASSES):
        data_2[i] = DS2_2[cls]

    CLASSES = sorted(DS2_1.keys())
    data_1 = np.empty((len(CLASSES), *list(DS2_1.values())[0].shape))
    for i, cls in enumerate(CLASSES):
        data_1[i] = DS2_1[cls]
