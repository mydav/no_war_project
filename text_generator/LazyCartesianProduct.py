import math


class LazyCartesianProduct:
    def __init__(self, sets):
        self.sets = sets
        self.divs = []
        self.mods = []
        self.maxSize = 1
        self.precompute()

    def precompute(self):
        for i in self.sets:
            self.maxSize = self.maxSize * len(i)
        length = len(self.sets)
        factor = 1
        for i in range((length - 1), -1, -1):
            items = len(self.sets[i])
            self.divs.insert(0, factor)
            self.mods.insert(0, items)
            factor = factor * items

    def entryAt(self, n):
        length = len(self.sets)
        if n < 0 or n >= self.maxSize:
            raise IndexError
        combination = []
        for i in range(0, length):
            combination.append(
                self.sets[i][int(math.floor(n / self.divs[i])) % self.mods[i]]
            )
        return combination


def LazyCartesianProductExample():
    """
        https://medium.com/hackernoon/generating-the-nth-cartesian-product-e48db41bed3f
    """
    a = [1, 2, 3, 4, 5]
    b = ["foo", "bar"]
    c = ["x", "y", "z"]
    d = ["one", "two", "three"]

    sets = [a, b, c, d]

    cp = LazyCartesianProduct(sets)

    result1 = cp.entryAt(8)
    print(result1)

    result2 = cp.entryAt(32)
    print(result2)

    result3 = cp.entryAt(67)
    print(result3)


if __name__ == "__main__":

    t = 1
    if t:
        LazyCartesianProductExample()
