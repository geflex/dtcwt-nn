from collections import namedtuple
from typing import Callable
from matplotlib import pyplot as plt
import numpy as np
from numpy.random import default_rng

import dtcwt

from tensorflow.keras.utils import to_categorical  # noqa

import features


def complex_plots(ax, t, sig):
    ax.plot(t, np.abs(sig), label='abs')
    ax.plot(t, np.real(sig), label='real')
    ax.plot(t, np.imag(sig), label='imag')
    ax.legend()


def annotate_line(xydata, ax=None, fmt='{:.2f}'):
    """xydata = Line2D.get_xydata()"""
    ax = ax or plt.gca()
    for x, y in xydata:
        ax.annotate(fmt.format(y),
                    (x, y),
                    textcoords="offset points",  # how to position the text
                    xytext=(0, 5),  # distance from text to points (x,y)
                    ha='center')


fourier_image = features.fourier
complex_fft_image = features.complex_fourier


# TODO: signal.find_peaks()


def dtcwt_highpasses3d(transform, ax, ghost=':'):
    """plots dtcwt highpasses on 3D axes"""
    max_len = len(transform.highpasses[0])
    for z, hp in enumerate(transform.highpasses):
        ys = np.abs(hp)
        xs = np.arange(0, max_len, max_len / len(ys))
        p = ax.plot(xs, ys, zs=z, zdir='y')
        if ghost:
            ax.plot([0, max_len], [0, 0], linestyle=ghost, zs=z, zdir='y', color=p[-1].get_color())

    ax.set_xlabel('X')
    ax.set_ylabel('Уровень')
    ax.set_zlabel('Амплитуда')


def dtcwt_highpasses2d(transform: dtcwt.Transform1d, axs):
    for i, (ax, hp) in enumerate(zip(axs, transform.highpasses)):
        ax.plot(np.abs(hp))
        ax.set_title(f'ВЧ {i}')

    if len(axs) >= len(transform.highpasses):
        axs[-1].plot(transform.lowpass)
        axs[-1].set_title('НЧ')


def extract_features(data, get_feature: Callable[[np.array], np.array]):
    feature = get_feature(data[0, 0])  # needed only for shape and dtype

    out_data = np.empty((*data.shape[:2], *feature.shape), feature.dtype)
    print('Out shape is', out_data.shape)

    for cls, cls_data in enumerate(data):
        print(f'processing class {cls}')
        for i, sample in enumerate(cls_data):
            out_data[cls, i] = get_feature(sample)
    return out_data


TrainTest = namedtuple('TrainTest', 'train_data, train_labels, val_data, val_labels')


def split_train_test(data: np.array, ratio=0.8):
    class_num, per_class, *feature_shape = data.shape

    n_train = round(ratio * per_class)

    # shuffle samples in each class to randomly
    # split them into train and validation data
    default_rng().shuffle(data, axis=1)

    train_data = data[:, :n_train, :, :]
    val_data = data[:, n_train:, :, :]

    train_labels = np.arange(class_num).repeat(train_data.shape[1])
    val_labels = np.arange(class_num).repeat(val_data.shape[1])

    train_labels = to_categorical(train_labels)
    val_labels = to_categorical(val_labels)

    train_data = train_data.reshape(-1, *feature_shape)
    val_data = val_data.reshape(-1, *feature_shape)

    return TrainTest(train_data, train_labels, val_data, val_labels)


def float_wav_array_to_int(arr):
    return (np.ones(arr.shape[0], dtype=np.int16) * (2**15-1) * arr).astype(np.int16)
