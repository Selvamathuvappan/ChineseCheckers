import math


def sign(n):
    return (n > 0) - (n < 0)


def get_spaced_around_spots(
    regions_range_per_player: int, regions_per_player: int, total_regions: int
):
    all_regions = list(range(total_regions))
    right = math.ceil((regions_range_per_player - 1) / 2)
    left = regions_range_per_player - right - 1
    first_player_regions_range = suffix_prefix_list(all_regions, left, right)
    return [
        first_player_regions_range[idx]
        for idx in get_spots(regions_range_per_player, regions_per_player)
    ]


def get_spots(n, k):
    if k == 1:
        return [(n - 1) // 2]
    n_gaps = k - 1
    spots_per_gap = (n - k) // (k - 1)
    total = k + n_gaps * spots_per_gap
    extras = n - total
    start = extras // 2
    return list(range(start, n, spots_per_gap + 1))[:k]


def suffix_prefix_list(L, l, r):
    suffix = L[-l:] if l > 0 else []
    prefix = L[1 : r + 1] if r > 0 else []
    return suffix + [L[0]] + prefix
