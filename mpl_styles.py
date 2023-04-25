from matplotlib import rcParams, font_manager
import matplotlib.pyplot as plt
from cycler import cycler
import numpy as np


# all vertical, in millimeters
list_sizes = {
    'A4': [210, 297],
}
MM_PER_INCH = 25.4
# В ГОСТе таблица занимает 55 мм; отступы рамки по горизонтали и вертикали равны 25 и 10 мм соответственно. 
# Еще сверху микроштуковина высотой 14мм и длиной 70мм.
gost_padding = np.array([25, 55 + 14])
list_sizes = {k: (np.array(v) - gost_padding) / MM_PER_INCH for k, v in list_sizes.items()}
list_sizes |= {f'{k}/2': (v * np.array([1, 0.5])) for k, v in list_sizes.items()}


common = {
    'axes.grid': True,
    'figure.figsize': list_sizes['A4/2'],
    'figure.dpi': 200,
    'image.interpolation': 'none',
    'image.aspect': 'auto',
}


presentation_cmap = plt.get_cmap('BuPu')  # GnBu, Blues

presentation = [
    'seaborn',
    {
        'font.family': 'Arial',
        'font.style': 'normal',
        'axes.grid': True,
        'axes.prop_cycle': cycler(linestyle=['-', '--'], color=['#4c72b0', presentation_cmap(0.85)]),
        'image.cmap': presentation_cmap,
    },
]


def load_gost_fonts():
    fonts = font_manager.findSystemFonts(fontpaths=None, fontext='ttf')
    gost_fonts = [f for f in fonts if 'GOST' in f or 'ГОСТ' in f]
    for font in gost_fonts:
        font_manager.fontManager.addfont(font)

# чертеж
# before use call load_gost_fonts
drawing = {
    'font.family': 'GOST type A',
    'font.style': 'italic',
}

diploma = [
    'grayscale', 
    {
        'font.family': 'Times New Roman',
        'axes.prop_cycle': cycler(linestyle=['-', '--', '.-', '.']),
        'figure.facecolor': 'white',
        'grid.color': 'gray',
    },
]

def test_cycler():
    style_test_x = np.arange(0, 2*np.pi, 0.01)
    for i in range(len(rcParams['axes.prop_cycle'])):
        i += 1
        plt.plot(np.sin(style_test_x/i))
    plt.title('Test')
    plt.ylabel('Title')
