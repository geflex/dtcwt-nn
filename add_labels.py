import matplotlib.pyplot as plt

SAMPLES = 'Отсчёты'
DEC_LEVEL = 'Уровень декомпозиции'
HZ = 'Частота, Гц'
SECONDS = 'Время, с'
AMPLITUDE = 'Амплитуда, отн.ед.'
INTENCIVITY = 'Интенсивность, отн.ед.'
EPOCH = 'Эпоха'
LOSS_LABEL = 'Потери'
ACC_LABEL = 'Точность'


def _create_labels_setter(xlabel, ylabel):
    def add_labels(ax=None):
        ax = ax or plt.gca()
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
    return add_labels


dwt = _create_labels_setter(SAMPLES, DEC_LEVEL)
spec = _create_labels_setter(SECONDS, HZ)
fourier = _create_labels_setter(HZ, INTENCIVITY)
time = _create_labels_setter(SECONDS, AMPLITUDE)
sample = _create_labels_setter(SAMPLES, AMPLITUDE)
loss = _create_labels_setter(EPOCH, LOSS_LABEL)
accuracy = _create_labels_setter(EPOCH, ACC_LABEL)
