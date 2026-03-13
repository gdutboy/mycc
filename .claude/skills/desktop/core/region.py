class InvalidRegionError(ValueError):
    pass


def normalize_region(region, screen):
    x, y, width, height = region
    if width <= 0 or height <= 0:
        raise InvalidRegionError("region width and height must be positive")

    screen_x, screen_y, screen_width, screen_height = screen
    left = max(x, screen_x)
    top = max(y, screen_y)
    right = min(x + width, screen_x + screen_width)
    bottom = min(y + height, screen_y + screen_height)

    clipped_width = right - left
    clipped_height = bottom - top
    if clipped_width <= 0 or clipped_height <= 0:
        raise InvalidRegionError("region is outside screen bounds")

    return [left, top, clipped_width, clipped_height]
