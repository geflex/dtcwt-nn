from pathlib import Path
import seaborn as sns
from matplotlib import pyplot as plt, rcParams
import numpy as np

from mpl_styles import list_sizes
import add_labels


HISTORY_FILENAME = 'history.npz'
ACCURACY_FILENAME = 'loss_accuracy.png'
CFMATR_FILENAME = 'cfmatr.png'


def save_history(history: dict, model_dir: Path):
    params = 'val_loss', 'loss', 'val_accuracy', 'accuracy'
    with open(model_dir / HISTORY_FILENAME, 'wb') as f:
        np.savez(f, **{p: history[p] for p in params})


def plot_history(history: dict, model_dir: Path):
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=list_sizes['A4']*np.array([0.66, 0.66]))

    ax1.plot(history['loss'], label='При обучении')
    ax1.plot(history['val_loss'], label='При валидации')
    add_labels.loss(ax1)
    ax1.legend()

    ax2.plot(history['accuracy'], label='При обучении')
    ax2.plot(history['val_accuracy'], label='При валидации')
    add_labels.accuracy(ax2)
    ax2.legend()

    fig.tight_layout()
    fig.savefig(model_dir / ACCURACY_FILENAME)


def plot_conf_matrix(conf_matrix, classes, model_dir: Path):
    ax = sns.heatmap(conf_matrix, annot=True, fmt='g', cmap=rcParams['image.cmap'],
                     square=True, cbar_kws={'label': 'Количество объектов', })
    ax.set_ylabel('Действительный класс')
    ax.set_xlabel('Предсказанный класс')
    ax.set_yticklabels(classes, rotation=0)
    ax.set_xticklabels(classes, rotation=45)
    plt.tight_layout()
    plt.savefig(model_dir / CFMATR_FILENAME)
