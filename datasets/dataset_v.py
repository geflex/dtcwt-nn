import scipy.io as sio
import numpy as np


PATH = './data/Dataset0/DataForClassification_TimeDomain.mat'
SAMPLE_LEN = 3600
CLASSES = ('healthy', 'missing', 'crack', 'spall',
           'chip5a', 'chip4a', 'chip3a', 'chip2a', 'chip1a')
CLASS_LEN = 104
FS = 20000
DT = 1 / FS


def load(filename=PATH, n_points=SAMPLE_LEN):
    data = sio.loadmat(filename)['AccTimeDomain'][:n_points, :]  # shape (3600, 936)
    return np.reshape(data, (SAMPLE_LEN, -1, len(CLASSES))).T  # t, samples, class
