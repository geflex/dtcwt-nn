import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvas

from widgets.gui_settings import GUIConfig
import add_labels


class Display2DWidget(FigureCanvas):
    def __init__(self, gui_config: GUIConfig):
        figure = Figure(layout='tight')

        self.image_settings = dict(
            cmap=gui_config.colormap,
            aspect='auto',
            interpolation='none',
        )
        self.settings = gui_config

        super().__init__(figure)
        self.dynamic_ax = self.figure.subplots()
        self.setup_ax(self.dynamic_ax)
        dummy_data = np.zeros((1, 1))
        self.dynamic_im = self.dynamic_ax.imshow(dummy_data, **self.image_settings)

    def setup_ax(self, ax):
        ax.set_axis_off()
        ax.margins(0)

    def update_image(self, arr: np.array):
        self.dynamic_im.set(data=arr, clim=(arr.min(), arr.max()), cmap=self.settings.colormap)
        # self.dynamic_im.figure.canvas.draw()
        self.draw()


class Display1DWidget(FigureCanvas):
    def __init__(self, epochs_count: int):  # TODO: add config
        self._epochs_count = epochs_count

        figure = Figure(layout='tight')
        super().__init__(figure)

        self.dynamic_ax = self.figure.subplots()
        self.setup_ax(self.dynamic_ax)

        dummy_data = np.zeros(np.array([0, 0.27, 0.49, 0.65]))
        self.dynamic_line = self.dynamic_ax.plot(dummy_data)

    def setup_ax(self, ax):
        pass

    def update_image(self, value):
        arr = np.append(self.dynamic_line.get_ydata(), value)
        self.epoch_loss_line.set(data=arr)


class LossPlotWidget(Display1DWidget):
    def setup_ax(self, ax):
        add_labels.loss(ax)
        return super().setup_ax(ax)


class AccPlotWidget(Display1DWidget):
    def setup_ax(self, ax):
        add_labels.accuracy(ax)
        return super().setup_ax(ax)
