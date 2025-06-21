import curses


class ColorManager:
    """
    Manages color schemes for different board regions in a curses-based UI.

    It assigns foreground and background color pairs, handles bold styling,
    and highlights points as needed. Internally caches initialized color pairs
    to ensure consistent color scheme and work within terminal color pair limitations.
    """

    _COLOR_PALETTE = [
        curses.COLOR_WHITE,  # region 0
        curses.COLOR_BLUE,
        curses.COLOR_CYAN,
        curses.COLOR_GREEN,
        curses.COLOR_MAGENTA,
        curses.COLOR_RED,
        curses.COLOR_YELLOW,
    ]

    def __init__(self) -> None:
        self._cache = {}
        self._next_id = 1
        self._max_pairs = 1 + (len(self._COLOR_PALETTE) - 1) * 2

    def get_region_style(self, region: int) -> tuple[int, bool]:
        """
        Determines the foreground color and bold style for a given region.
        """
        if region == 0:
            return curses.COLOR_WHITE, False
        palette_size = len(self._COLOR_PALETTE) - 1  # exclude white at index 0
        index = region - 1
        color = self._COLOR_PALETTE[(index % palette_size) + 1]
        bold = index >= palette_size
        return color, bold

    def color_pair(self, fg: int, bg: int = curses.COLOR_BLACK) -> int:
        """
        Retrieves or creates a curses color pair.
        """
        key = (fg, bg)
        if key in self._cache:
            return self._cache[key]

        if self._next_id > self._max_pairs:
            raise RuntimeError("Exceeded maximum color pairs supported by terminal.")

        curses.init_pair(self._next_id, fg, bg)
        pair = curses.color_pair(self._next_id)
        self._cache[key] = pair
        self._next_id += 1
        return pair

    def __call__(self, region: int, highlight: bool = False) -> int:
        """
        Computes the display attribute for a given region and highlight flag.
        """
        fg, bold = self.get_region_style(region)
        attr = self.color_pair(fg)
        if bold:
            attr |= curses.A_BOLD
        if highlight:
            attr |= curses.A_REVERSE
        return attr


color_manager = ColorManager()
del ColorManager
