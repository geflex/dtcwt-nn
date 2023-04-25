import numpy as np
import matplotlib.pyplot as plt


def mexmor(t):
    k = 5 / np.pi

    t1 = t[t <= 0]
    x1 = np.exp((2*k*t1)**2 / -2) * (1 - (k*t1)**2)

    t2 = t[t > 0]
    x2 = np.exp(t2**2 / -2) * np.cos(5*t2)
    return np.concatenate((x1, x2))


def cosines(t):
    t1 = t[t <= 0]
    x1 = np.exp(-16 * t1**2) * np.cos(5*t1)

    t2 = t[t > 0]
    x2 = np.exp(t2**2 / -3) * np.cos(5*t2)
    return np.concatenate((x1, x2))


def plot_wavelets(wavelets=(mexmor, cosines)):
    t = np.linspace(-5, 5, 200)
    for wavelet in wavelets:
        plt.plot(t, wavelet(t))
    plt.show()
