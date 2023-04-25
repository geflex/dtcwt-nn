import numpy as np
import matplotlib.pyplot as plt
import scipy.signal as signal


def morlet_3d():
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    N = 200
    t = np.linspace(0, 1, N)
    wavelet = signal.morlet2(N, 30)
    ys = np.real(wavelet)
    zs = np.imag(wavelet)
    ax.plot(t, ys, zs)
    ax.plot(t, ys, zs=zs.min())
    ax.plot(t, zs, zs=ys.min(), zdir='y')
    ax.set_box_aspect((.3, np.ptp(ys), np.ptp(zs)))  # aspect ratio is 1:1:1 in data space

    ax.set_xlabel('time')
    ax.set_ylabel('real')
    ax.set_zlabel('imag')


if __name__ == '__main__':
    morlet_3d()
    plt.show()
