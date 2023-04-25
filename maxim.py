import itertools
import inspect
import math
import sys
import time

import numpy as np
from matplotlib.backends.backend_qtagg import FigureCanvas
from matplotlib.figure import Figure
from PyQt6.QtCore import QThread, pyqtSignal, QObject
from PyQt6.QtWidgets import (QApplication, QDoubleSpinBox, QFormLayout,
                             QGridLayout, QHBoxLayout, QMainWindow,
                             QProgressBar, QPushButton, QVBoxLayout, QWidget)


def get_param_default(func, param_name):
    return inspect.signature(func).parameters[param_name].default


def oscillator(t, x, v, omega_0=1, delta_0=0, omega=1.1, Amp=1, alpha=0, beta=0):
    return Amp * math.sin(omega * t) - omega_0 ** 2 * x - 2 * delta_0 * v - beta * x ** 3 - alpha * x ** 2 - math.sin(x)


def rk2(f, x_0, v_0, step, **kwargs):
    j_1, j_2 = 0, 0
    k_1, k_2 = 0, 0
    v = v_0
    x = x_0

    for t in itertools.count(0, step):
        v = v + j_2
        x = x + k_2
        j_1 = step * f(t, x, v, **kwargs)
        k_1 = step * v
        j_2 = step * f(t + 0.5 * step, x + 0.5 * k_1, v + 0.5 * j_1, **kwargs)
        k_2 = step * (v + 0.5 * j_1)

        yield t, x, v


def fourier(xs, dt):
    xf = np.fft.rfftfreq(len(xs), dt)
    yf = 2.0 / len(xs) * np.abs(np.fft.rfft(xs))
    return xf, yf


def add_worker_to_thread(thread: QThread, worker: QObject):
    worker.moveToThread(thread)
    thread.started.connect(worker.run)
    worker.finished.connect(thread.quit)

    worker.finished.connect(worker.deleteLater)
    thread.finished.connect(thread.deleteLater)


class RK2Thread(QThread):
    finished = pyqtSignal()
    iteration_passed = pyqtSignal(float, float, float)

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent)
        self._paused = False
        self.args = args
        self.kwargs = kwargs

    def run(self):
        for t, x, v in rk2(oscillator, *self.args, **self.kwargs):
            self.iteration_passed.emit(t, x, v)
            self.msleep(50)


class PlotWidget(FigureCanvas):
    def __init__(self, draw_time_period=0.1):
        figure = Figure(layout='tight')

        super().__init__(figure)
        self.draw_time_period = draw_time_period
        self._last_draw_time = 0
        self._dynamic_ax = self.figure.subplots()
        self._setup_ax()
        self._dynamic_line = None
        self.clear()

    @property
    def ax(self):
        return self._dynamic_ax

    def _setup_ax(self):
        self._dynamic_ax.margins(0)

    def _update_minmax(self, x, y):
        if self._xmin is None:
            self._xmin, self._xmax = x, x
            self._ymin, self._ymax = y, y
        else:
            if x < self._xmin:
                self._xmin = x
            elif x > self._xmax:
                self._xmax = x
            if y < self._ymin:
                self._ymin = y
            elif y > self._ymax:
                self._ymax = y

    def append_data(self, x: float, y: float):
        self._update_minmax(x, y)
        self._dynamic_ax.set_xlim(self._xmin, self._xmax)
        self._dynamic_ax.set_ylim(self._ymin, self._ymax)
        xdata, ydata = self._dynamic_line.get_data(orig=True)
        self._dynamic_line.set_data([np.append(xdata, x), np.append(ydata, y)])
        self.draw_timed()

    def plot(self, xs, ys):
        self.clear(xs, ys)

    def draw_timed(self):
        current_time = time.time()  # there is no high precision given by time_ns() needed
        if current_time - self._last_draw_time > self.draw_time_period:
            self.draw()
            self._last_draw_time = current_time

    def clear(self, xs=(), ys=()):
        if self._dynamic_line is not None:
            self._dynamic_line.remove()
        self._dynamic_line = self._dynamic_ax.plot(xs, ys)[0]
        self._xmin, self._xmax = None, None
        self._ymin, self._ymax = None, None

    def get_ydata(self):
        return self._dynamic_line.get_ydata()


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.rk2_thread, self.rk2_thread = None, None
        self.main_layout = self.init_main_layout()
        self.main_widget = QWidget()
        self.main_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.main_widget)

    def init_main_layout(self):
        main_layout = QVBoxLayout()
        self.plots_grid = self.init_plots()
        self.input_pane = self.init_input_pane()
        self.buttons_pane = self.init_buttons_pane()
        self.fft_button_pane = self.init_fft_button_pane()

        inputs_fftbutton_layout = QVBoxLayout()
        inputs_fftbutton_layout.addLayout(self.input_pane)
        inputs_fftbutton_layout.addLayout(self.fft_button_pane)

        plots_inputs_fft_button_layout = QHBoxLayout()
        plots_inputs_fft_button_layout.addLayout(self.plots_grid)
        plots_inputs_fft_button_layout.addLayout(inputs_fftbutton_layout)

        main_layout.addLayout(plots_inputs_fft_button_layout)
        main_layout.addLayout(self.buttons_pane)

        return main_layout

    def init_plots(self):
        self.plot_x_t = PlotWidget(draw_time_period=.5)
        self.plot_v_t = PlotWidget(draw_time_period=.5)
        self.plot_x_v = PlotWidget(draw_time_period=.5)
        self.plot_fourier = PlotWidget(draw_time_period=.5)

        self.plot_x_t.ax.set_title("X(t)")
        self.plot_v_t.ax.set_title("V(t)")
        self.plot_x_v.ax.set_title("V(X)")
        self.plot_fourier.ax.set_title("FFT")

        self.plot_x_t.ax.set_xlabel('Time')
        self.plot_v_t.ax.set_xlabel('Time')
        self.plot_x_v.ax.set_ylabel('X')
        self.plot_fourier.ax.set_ylabel('ω')

        grid = QGridLayout()
        grid.addWidget(self.plot_x_t, 0, 0)
        grid.addWidget(self.plot_v_t, 0, 1)
        grid.addWidget(self.plot_x_v, 1, 0)
        grid.addWidget(self.plot_fourier, 1, 1)

        return grid

    def init_input_pane(self):
        input_pane = QFormLayout()
        self.input_x0 = QDoubleSpinBox()
        self.input_v0 = QDoubleSpinBox()
        self.input_omega0 = QDoubleSpinBox()
        self.input_delta0 = QDoubleSpinBox()
        self.input_omega = QDoubleSpinBox()
        self.input_amplitude = QDoubleSpinBox()
        self.input_alpha = QDoubleSpinBox()
        self.input_beta = QDoubleSpinBox()
        self.input_step = QDoubleSpinBox()

        self.input_x0.setValue(0)
        self.input_v0.setValue(1)
        self.input_step.setValue(.1)

        # retrieve params values from `oscillator` and set them as default input values
        for inp, param in (
            (self.input_omega0, 'omega_0'),
            (self.input_delta0, 'delta_0'),
            (self.input_omega, 'omega'),
            (self.input_amplitude, 'Amp'),
            (self.input_alpha, 'alpha'),
            (self.input_beta, 'beta'),
        ):
            inp.setValue(get_param_default(oscillator, param))

        input_pane.addRow("X₀", self.input_x0)
        input_pane.addRow("V₀", self.input_v0)
        input_pane.addRow("ω₀", self.input_omega0)
        input_pane.addRow("δ₀", self.input_delta0)
        input_pane.addRow("ω", self.input_omega)
        input_pane.addRow("Amplitude A", self.input_amplitude)
        input_pane.addRow("Coeff. α", self.input_alpha)
        input_pane.addRow("Coeff. β", self.input_beta)
        input_pane.addRow("Time step dt", self.input_step)

        return input_pane

    def init_buttons_pane(self):
        layout = QHBoxLayout()
        self.start_button = QPushButton('Start')
        self.start_button.setShortcut('F5')
        self.start_button.setCheckable(True)
        # self.terminate_button = QPushButton('Terminate')

        layout.addWidget(self.start_button)
        # layout.addWidget(self.terminate_button)

        self.start_button.clicked.connect(self.run)

        return layout

    def run_fft(self, ydata):
        step = self.input_step.value()
        x, y = fourier(ydata, step)
        self.plot_fourier.plot(x, y)
        self.plot_fourier.draw()

    def init_fft_button_pane(self):
        layout = QVBoxLayout()
        self.fft_button_xt = QPushButton('FFT[x(t)]')
        self.fft_button_vt = QPushButton('FFT[v(t)]')
        self.fft_button_xt.clicked.connect(lambda: self.run_fft(self.plot_x_t.get_ydata()))
        self.fft_button_vt.clicked.connect(lambda: self.run_fft(self.plot_v_t.get_ydata()))

        layout.addWidget(self.fft_button_xt)
        layout.addWidget(self.fft_button_vt)
        return layout

    def run(self):
        if self.rk2_thread is None:
            self.start_button.setText('Stop')
            self.plot_v_t.clear()
            self.plot_x_t.clear()
            self.plot_x_v.clear()
            self.rk2_thread = self.init_rk2_worker()
            self.rk2_thread.start()
            self.rk2_thread.setTerminationEnabled(True)
        else:
            self.rk2_thread.terminate()
            self.start_button.setText('Start')
            # self.rk2_worker.soft_stop()
            self.rk2_thread = None
        self.start_button.setShortcut('F5')

    def init_rk2_worker(self):
        thread = RK2Thread(
            parent=self,
            x_0=self.input_x0.value(),
            v_0=self.input_v0.value(),
            step=self.input_step.value(),
            omega_0=self.input_omega0.value(),
            delta_0=self.input_delta0.value(),
            omega=self.input_omega.value(),
            Amp=self.input_amplitude.value(),
            alpha=self.input_alpha.value(),
            beta=self.input_beta.value(),
        )
        thread.iteration_passed.connect(lambda t, x, v: self.plot_v_t.append_data(t, v))
        thread.iteration_passed.connect(lambda t, x, v: self.plot_x_t.append_data(t, x))
        thread.iteration_passed.connect(lambda t, x, v: self.plot_x_v.append_data(v, x))
        return thread


def main():
    app = QApplication(sys.argv)
    ui = MainWindow()
    ui.show()
    app.exec()


if __name__ == '__main__':
    main()
    # for t, x, v in rk2(oscillator, 0, 1, .1):
    #     print(t, x, v)
