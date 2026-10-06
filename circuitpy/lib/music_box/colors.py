"""Colors for the keys. Every key has its own rainbow hue."""

OFF = (0, 0, 0)
WHITE = (255, 255, 255)


def wheel(pos):
    """Map 0-255 around the color wheel: red -> green -> blue -> red."""
    pos = pos % 256
    if pos < 85:
        return (255 - pos * 3, pos * 3, 0)
    if pos < 170:
        pos -= 85
        return (0, 255 - pos * 3, pos * 3)
    pos -= 170
    return (pos * 3, 0, 255 - pos * 3)


def key_color(key):
    """Red at the low (top-left) key through violet at the high one."""
    return wheel(key * 200 // 11)


def dim(color, factor=0.08):
    return tuple(int(c * factor) for c in color)
