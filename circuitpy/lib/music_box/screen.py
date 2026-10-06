"""Draws a mode icon, a big setting icon, and position dots on the OLED.

+-------------------------------+
|        +-----------+          |
| [mode] |  setting  |          |
|        +-----------+          |
|          o o * o              |
+-------------------------------+
"""

import displayio

from music_box.icons import ICONS, SIZE

DOT = 4
DOT_GAP = 4
DOTS_Y = 57


class Screen:
    def __init__(self, display):
        self.display = display
        self.palette = displayio.Palette(2)
        self.palette[0] = 0x000000
        self.palette[1] = 0xFFFFFF
        self.bitmaps = {}

        self.mode_icon = displayio.Group(scale=2, x=4, y=12)
        self.setting_icon = displayio.Group(scale=3, x=56, y=2)
        self.dots = displayio.Bitmap(display.width, DOT, 2)

        self.root = displayio.Group()
        self.root.append(self.mode_icon)
        self.root.append(self.setting_icon)
        self.root.append(displayio.TileGrid(self.dots, pixel_shader=self.palette, y=DOTS_Y))
        self.blank = displayio.Group()
        display.root_group = self.root

    def bitmap(self, name):
        if name not in self.bitmaps:
            bmp = displayio.Bitmap(SIZE, SIZE, 2)
            for y, row in enumerate(ICONS[name]):
                for x, ch in enumerate(row):
                    if ch == "#":
                        bmp[x, y] = 1
            self.bitmaps[name] = bmp
        return self.bitmaps[name]

    def _set(self, group, name):
        while len(group):
            group.pop()
        if name:
            group.append(displayio.TileGrid(self.bitmap(name), pixel_shader=self.palette))

    def show(self, mode_icon, setting_icon, index, count):
        self._set(self.mode_icon, mode_icon)
        self._set(self.setting_icon, setting_icon)
        self.dots.fill(0)
        if count > 1:
            width = count * DOT + (count - 1) * DOT_GAP
            left = 56 + (SIZE * 3 - width) // 2
            for i in range(count):
                x0 = left + i * (DOT + DOT_GAP)
                for x in range(x0, x0 + DOT):
                    for y in range(DOT):
                        # The current position is a filled square; the rest are outlines.
                        edge = x in (x0, x0 + DOT - 1) or y in (0, DOT - 1)
                        if i == index or edge:
                            self.dots[x, y] = 1

    def sleep(self):
        self.display.root_group = self.blank

    def wake(self):
        self.display.root_group = self.root
