import numpy as np
import scipy.fft as fft
from scipy import signal
import pywt
from dtcwt import Transform1d, defaults as dtcwt_defaults
# from dtcwt.numpy.lowlevel import colfilter, coldfilt


# TODO mlab.magnitude spectrum
# TODO: psd, csd, dct, dst, fast hankel


def normalize(data):
    return (data - data.min()) / (data.max() - data.min())


def dtcwt_shape(fragment_len, levels, include_orig, include_cj):
    h = levels + include_orig + include_cj
    w = fragment_len if include_orig else fragment_len // 2
    return h, w


def dtcwt(sample, levels: int, include_orig: bool, include_cj: bool,
          biort=dtcwt_defaults.DEFAULT_BIORT,
          qshift=dtcwt_defaults.DEFAULT_QSHIFT):
    h, w = dtcwt_shape(len(sample), levels, include_orig, include_cj)
    transform = Transform1d(biort, qshift).forward(sample, nlevels=levels)
    im = np.empty((h, w), dtype=sample.dtype)
    if include_orig:
        im[0] = sample
    for i, hp in enumerate(transform.highpasses, start=include_orig):
        im[i] = np.abs(hp).repeat(2**i)
    if include_cj:
        r = w // len(transform.lowpass)
        im[-1] = np.abs(transform.lowpass).repeat(r)
    return normalize(im)


def dwt(sample, wavelet, level):
    cA, *cD = pywt.wavedec(sample, wavelet, level=level)
    width = len(sample) // 2
    arr = np.ndarray((level, width), dtype=cA.dtype)
    for j, cDj in enumerate(reversed(cD)):
        arr[j] = np.repeat(cDj, 2**j)[:width]
    return arr


def dtcwt_1d_optimized(X, nlevels=1, near_sym=None, qshift=None):
    """
    There are no checks, but
    * len(x) must be a power of 2
    * nlevels must be greater than 0
    """
    # Yh = np.empty((nlevels+1, len(X)), dtype=X.dtype)
    # Yh[0] = X

    # # Level 1.
    # Hi = colfilter(X, h1o)
    # Lo = colfilter(X, h0o)
    # Yh[1] = np.abs(Hi[::2,:] + 1j*Hi[1::2,:]).repeat(2)

    # # Levels 2 and above.
    # for level in range(2, nlevels+1):
    #     Hi = coldfilt(Lo, h1b, h1a)
    #     Lo = coldfilt(Lo, h0b, h0a)

    #     Yh[level] = np.abs(Hi[::2, :] + 1j*Hi[1::2, :]).repeat(2**level)

    # return Yh
    raise NotImplementedError


def fourier_shape(signal_len: int):
    return signal_len // 2


def fourier(xs: np.array, dt):
    xf = fft.rfftfreq(len(xs), dt)
    yf = 2.0 / len(xs) * np.abs(fft.rfft(xs))
    return xf, yf


def complex_fourier(xs, dt):
    xf = fft.fftfreq(len(xs), dt)
    yf = 2.0 / len(xs) * np.abs(fft.fft(xs))
    return xf, yf


def cwt_morlet(sample, fs: int, w=6., freq_num=31):
    """
    sample: 1d array
    fs: sample rate, hz
    return: array[array[complex]]
    """
    freqs = np.linspace(1, fs/2, freq_num)
    widths = w*fs / (2*freqs*np.pi)
    # noinspection PyTypeChecker
    return signal.cwt(sample, signal.morlet2, widths, w=w)


def cwt_ricker(sample, nwidths=25, max_width=400):
    """
    sample: 1d array
    return: array[array[real]]
    """
    widths = np.linspace(1, max_width, nwidths)
    # noinspection PyTypeChecker
    return signal.cwt(sample, signal.ricker, widths)
