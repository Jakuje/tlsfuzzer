import random

class StructuredRandom(object):
    def __init__(self, vals, rng=None):
        self.vals = vals
        if not rng:
            rng = random
        self.rng = rng

    @property
    def data(self):
        ret = bytearray()
        for length, content in self.vals:
            if content is None:
                ret += bytearray(self.rng.randint(0, 255) for _ in range(length))
            else:
                ret += bytearray([content] * length)
        return ret

    def __repr__(self):
        return "StructuredRandom(vals={0})"\
               .format(self.vals)


def _normalise_groups(groups, sum_len, step):
    """Make sure the sum of all lengths in groups is a multiple of step."""
    if sum_len % step:
        for i, val in enumerate(groups):
            if val[0] > (sum_len % step):
                groups[i] = (val[0] - (sum_len % step), val[1])
                sum_len -= sum_len % step
                break

    # in case the list or all elements are super short
    if sum_len % step:
        groups[0] = (groups[0][0] + step - (sum_len % step),
                     groups[0][1])
        return


def structured_random_iter(count=100, min_length=1, max_length=2**16, step=1):
    """
    Iterator that returns a random StructuredRandom object.

    Useful as a payload for TLS message plaintext
    """
    rng = random.SystemRandom()
    max_length = rng.randint(min_length, max_length)
    for _ in range(count):
        no_groups = int(rng.gammavariate(2, 2)) + 1
        no_groups = min(max_length, no_groups)

        groups = []
        sum_len = 0
        for i in range(no_groups):
            group_min = 1
            group_max = max_length - sum_len - (no_groups - i - 1)
            # generate short elements sometimes
            if rng.choice([True, False]):
                length = rng.randint(group_min, group_max)
            else:
                length = rng.randint(group_min,
                                     max(group_min, group_max // 10))
            # generate different looking strings
            if rng.choice([True, False, False, False]):
                groups.append((length, None))
            elif rng.choice([True, False, False]) and length < 256:
                groups.append((length, length - 1))
            else:
                groups.append((length, rng.randint(0, 255)))
            sum_len += length

        _normalise_groups(groups, sum_len, step)

        yield StructuredRandom(groups)
