"""

"""
import random


class CrazyPlane:
    """
    plane coordinates
    """
    def __init__(self, x=0, y=0):
        """
        x coordinate
        y coordinate
        """
        self.x = x
        self.y = y

    def get_position(self):
        """
        returns the coordinates of the plane
        """
        return self.x, self.y

    def __str__(self):
        """
        returns the coordinates of the plane
        """
        return "Coordinates: " + "%d, %d" % (self.x, self.y) + " str"

    def __repr__(self):
        """
        returns the coordinates of the plane
        """
        return "Coordinates: " + "%d, %d" % (self.x, self.y) + " repr"


def main():
    planes = []
    for i in range(5):
        plane = CrazyPlane(random.randint(-1, 1), random.randint(-1,1))
        planes.append(plane)
        print(plane)
    print(planes)


if __name__ == '__main__':
    main()
