import numpy as np
from PyQt6.QtWidgets import QVBoxLayout, QWidget, QMainWindow
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
from matplotlib.path import Path
from matplotlib.patches import PathPatch
from matplotlib.ticker import MaxNLocator


class BarMultiplier(QVBoxLayout):
    def __init__(
        self,
        parent: QMainWindow | QWidget,
        multipliers: list[float],
        max_multipliers: int = 18
    ):
        super().__init__(parent)
        self.max_multipliers = max_multipliers
        self.bar_heights = []
        self.bar_colors = []
        self.bar_width = 0.9
        fig, ax = plt.subplots()
        plt.margins(x=0, y=0.03, tight=False)
        fig.set_figwidth(parent.geometry().width() / 100)
        fig.set_figheight(parent.geometry().height() / 100)
        fig.tight_layout()
        fig.set_facecolor("#474747")
        ax.set_facecolor("#000000")
        ax.yaxis.set_major_locator(MaxNLocator(integer=True, nbins=10))
        ax.xaxis.set_major_locator(MaxNLocator(integer=True, nbins=10))
        self.canvas = FigureCanvas(fig)
        # self.canvas_layout.addWidget(self.canvas)
        self.addWidget(self.canvas)
        # Add a bar chart to the plot
        self.bar_heights = []
        self.bar_colors = []
        self.x_data = []
        self.add_multipliers(multipliers)
        ax_box = ax.get_position()
        x0 = 0.05
        y0 = 0.05
        x1 = 0.92
        y1 = 0.92
        ax.set_position((x0, y0, x1, y1))
        # ax.legend()

    def draw(self):
        self.canvas.draw()

    def __get_bar_height(self, multipliers: list[float]):
        bar_height = self.bar_heights or []
        if bar_height:
            bar_height.pop(0)
        for multiplier in multipliers:
            value = 1 if multiplier >= 2 else -1
            last_value = 0 if len(bar_height) == 0 else bar_height[-1]
            value_ = last_value + value
            bar_height.append(value_)
        return bar_height

    def __get_bar_color(self, multipliers: list[float]):
        # use https://matplotlib.org/stable/gallery/color/named_colors.html
        bar_colors = self.bar_colors or []
        if bar_colors:
            bar_colors.pop(0)
        for multiplier in multipliers:
            if multiplier < 2:
                bar_colors.append("deepskyblue")
            elif 2 <= multiplier < 10:
                bar_colors.append("darkviolet")
            else:
                bar_colors.append("crimson")
        return bar_colors

    """def add_multipliers(self, multipliers: list[float]):
        if not multipliers:
            return
        # Append the new height to the list of bar heights
        if len(multipliers) > self.max_multipliers:
            multipliers = multipliers[-self.max_multipliers:]
        self.bar_heights = self.__get_bar_height(multipliers)
        self.bar_colors = self.__get_bar_color(multipliers)
        self.x_data = [i + 1 for i in range(len(self.bar_heights))]
        ax = self.canvas.figure.axes[0]
        ax.clear()
        ax.set_xlim(0.5, len(self.bar_heights) + 0.5)
        ax.set_xticks([])
        ax.plot(self.x_data, self.bar_heights, color='w')  # , marker='o', markersize=1, markeredgecolor='k')
        ax.bar(self.x_data, self.bar_heights, self.bar_width, color=self.bar_colors, capstyle='round')
        ax.grid(axis='y', color='gray', linestyle='dashed', linewidth=0.4)
        self.draw()"""

    def add_multipliers(self, multipliers: list[float]):
        if not multipliers:
            return
        if len(multipliers) > self.max_multipliers:
            multipliers = multipliers[-self.max_multipliers:]
        self.bar_heights = self.__get_bar_height(multipliers)
        self.bar_colors = self.__get_bar_color(multipliers)
        self.x_data = [i + 1 for i in range(len(self.bar_heights))]
        ax = self.canvas.figure.axes[0]
        ax.clear()
        ax.set_xlim(-0.1, len(self.bar_heights) + 0.5)
        ax.set_xticks([])
        for i, (cat, val) in enumerate(zip(self.x_data, self.bar_heights)):
            bar_patch = self.round_bar(i, 0, 1, val, 0.5, self.bar_colors[i])
            ax.add_patch(bar_patch)
        x_line = np.arange(len(self.x_data)) + 0.5
        ax.plot(x_line, self.bar_heights, color='w', marker='o', markersize=1)
        ax.grid(axis='y', color='gray', linestyle='dashed', linewidth=0.4)
        self.draw()

    @staticmethod
    def round_bar(x, y, width, height, radius=0.4, color='skyblue'):
        left, right = x, x + width
        bottom, top = y, y + height
        path_ = [
            (left, bottom),
            (right, bottom), (right, bottom), (right, bottom),
            (right, top), (right, top), (right, top),
            (left, top), (left, top), (left, top),
            (left, bottom)
        ]
        if height > 0:
            path_ = [
                (left, bottom),
                (right, bottom), (right, bottom), (right, bottom),
                (right, top - radius), (right, top), (right - radius, top),
                (left + radius, top), (left, top), (left, top - radius),
                (left, bottom)
            ]
        elif height < 0:
            path_ = [
                (left, bottom),
                (right, bottom), (right, bottom), (right, bottom),
                (right, top + radius), (right, top), (right - radius, top),
                (left + radius, top), (left, top), (left, top + radius),
                (left, bottom)
            ]
        path = Path(path_, [ # NOQA
            Path.MOVETO,
            Path.LINETO, Path.CURVE3, Path.CURVE3,
            Path.LINETO, Path.CURVE3, Path.CURVE3,
            Path.LINETO, Path.CURVE3, Path.CURVE3,
            Path.LINETO,
        ])
        return PathPatch(path, facecolor=color, edgecolor='k')
