import time
import atexit
import random
from collections import deque
from threading import Thread

import digitalio
import board
import adafruit_rgb_display.st7789 as st7789

from PIL import Image, ImageDraw#, ImageFont
import matplotlib.pyplot as plt

class Ui():
    PLOT_CONFIG = {
        'title' : 'DATA',
        'ylim' : (0, 100),
        'line_config' : (
            {'color' : '#0000FF', 'width' : 2},
            { },
            )
    }

    def __init__(self, refresh_rate=0.5, data_points=61):
        self._disp = st7789.ST7789(board.SPI(), baudrate=64000000,
                                   cs=digitalio.DigitalInOut(board.D4), 
                                   dc=digitalio.DigitalInOut(board.D5),
                                   rst=digitalio.DigitalInOut(board.D6),                                   
                                   width=135, height=240, x_offset=53, y_offset=40)

        self._height = self._disp.width   # we swap height/width to rotate it to landscape!
        self._width = self._disp.height
        self._image = Image.new('RGB', (self._width, self._height))
        self._rotation = 90
        self._draw = ImageDraw.Draw(self._image)
        self._draw.rectangle((0, 0, self._width, self._height), outline=0, fill=0)
        self._disp.image(self._image, self._rotation)
        #self._font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 24)

        x_time = [x * refresh_rate for x in range(data_points)]
        x_time.reverse()

        self._y_data = [ [deque([None] * data_points, maxlen=data_points) for _ in Ui.PLOT_CONFIG['line_config']] ]
        plt.style.use('dark_background')
        fig, self._ax = plt.subplots(figsize=(self._disp.width / 100, self._disp.height / 100))
        self._ax.xaxis.set_ticklabels([])
        self._ax.grid(True, linestyle=':')
        self._ax.set_xlim(min(x_time), max(x_time))
        self._ax.invert_xaxis()
        if 'title' in Ui.PLOT_CONFIG:
            self._ax.set_title(Ui.PLOT_CONFIG['title'], position=(0.5, 0.8))
        if 'ylim' in Ui.PLOT_CONFIG:
            self._ax.set_ylim(Ui.PLOT_CONFIG['ylim'])

        self._plot_lines = []
        for index, line_config in enumerate(Ui.PLOT_CONFIG['line_config']):
            line, = self._ax.plot(x_time, self._y_data[index])
            if 'color' in line_config:
                line.set_color(line_config['color'])
            if 'width' in line_config:
                line.set_linewidth(line_config['width'])
            if 'style' in line_config:
                line.set_linestyle(line_config['style'])
            self._plot_lines.append(line)

        self._t_poll = None
        self._running = False
        self._refresh_rate = refresh_rate

        atexit.register(self._cleanup)

    def update_data(self):
        for data in self._y_data[0]:
            data.append(random.random())

    def update_plot(self):
        # update lines with latest data
        for plot, lines in enumerate(self._plot_lines):
            for index, line in enumerate(lines):
                line.set_ydata(self._y_data[plot][index])
            # autoscale if not specified
            if 'ylim' not in Ui.PLOT_CONFIG.keys():
                self._ax.relim()
                self._ax.autoscale_view()
        # draw the plots
        canvas = plt.get_current_fig_manager().canvas
        plt.tight_layout()
        canvas.draw()
        # transfer into PIL image and display
        image = Image.frombytes('RGB', canvas.get_width_height(),
                                canvas.tostring_rgb())
        self._disp.image(image, self._rotation)

    def start_drawing(self):
        if self._t_poll is None:
            self._t_poll = Thread(target=self._run)
            self._t_poll.daemon = True
            self._t_poll.start()

    def stop_drawing(self):
        if self._t_poll is not None:
            self._running = False
            self._t_poll.join()

    def _cleanup(self):
        self.stop_drawing()

    def _run(self):
        self._running = True

        while self._running:
            #self._draw.rectangle((0, 0, self._width, self._height), outline=0, fill=0)
            #self._disp.image(self._image, self._rotation)
            self.update_data()
            self.update_plot()
            time.sleep(self._refresh_rate)
