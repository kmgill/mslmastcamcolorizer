
import os
import sys

from PIL import Image


class SourceImage:
    def __init__(self, path):
        self.img = Image.open(path)
        self.data = self.img.getdata()
        self.width = self.img.width
        self.height = self.img.height

    def get_pixel(self, x, y):
        if x < 0 or x >= self.width:
            raise Exception()
        elif y < 0 or y >= self.height:
            raise Exception()

        return self.data[x + (y * self.width)]

    @staticmethod
    def is_red_pixel(x, y):
        if not y % 2 == 0:
            return False
        if not x % 2 == 0:
            return False
        return True

    @staticmethod
    def is_green_pixel(x, y):
        if not x % 2 == 0 and y % 2 == 0:
            return True
        if x % 2 == 0 and not y % 2 == 0:
            return True
        return False

    @staticmethod
    def is_blue_pixel(x, y):
        if y % 2 == 0 :
            return False
        if x % 2 == 0:
            return False
        return True

    @staticmethod
    def __linear_interp(v0, v1, f):
        return (v0 * f) + (v1 * (1.0 - f))

    @staticmethod
    def __bilinear_interp(v00, v01, v10, v11, fv, fh):
        v0 = ((v00 * fh) + (v01 * (1.0 - fh)))
        v1 = ((v10 * fh) + (v11 * (1.0 - fh)))
        return SourceImage.__linear_interp(v0, v1, fv)

    def get_red(self, x, y):
        if x == 0 or x == self.width - 1:
            return 0
        elif y == 0 or y == self.height - 1:
            return 0
        elif self.is_red_pixel(x, y):
            return self.get_pixel(x, y)
        elif y % 2 == 0 and not x % 2 == 0: # Between red pixels horizontally
            r0 = float(self.get_pixel(x - 1, y))
            r1 = float(self.get_pixel(x + 1, y))
            return int(round(self.__linear_interp(r0, r1, .5)))
        elif not y % 2 == 0 and x % 2 == 0: # Between red pixels vertically
            r0 = float(self.get_pixel(x, y - 1))
            r1 = float(self.get_pixel(x, y + 1))
            return int(round(self.__linear_interp(r0, r1, .5)))
        elif self.is_blue_pixel(x, y):
            r00 = float(self.get_pixel(x - 1, y - 1))
            r01 = float(self.get_pixel(x + 1, y - 1))
            r10 = float(self.get_pixel(x - 1, y + 1))
            r11 = float(self.get_pixel(x + 1, y + 1))
            return int(round(self.__bilinear_interp(r00, r01, r10, r11, 0.5, 0.5)))
        else:
            return 0

    def get_green(self, x, y):
        if x == 0 or x == self.width - 1:
            return 0
        elif y == 0 or y == self.height - 1:
            return 0
        elif self.is_green_pixel(x, y):
            return self.get_pixel(x, y)
        elif self.is_red_pixel(x, y) or self.is_blue_pixel(x, y):
            r00 = float(self.get_pixel(x - 1, y))
            r01 = float(self.get_pixel(x, y - 1))
            r10 = float(self.get_pixel(x + 1, y))
            r11 = float(self.get_pixel(x, y + 1))
            return int(round(self.__bilinear_interp(r00, r01, r10, r11, 0.5, 0.5)))
        else:
            return 0

    def get_blue(self, x, y):
        if x == 0 or x == self.width - 1:
            return 0
        elif y == 0 or y == self.height - 1:
            return 0
        elif self.is_blue_pixel(x, y):
            return self.get_pixel(x, y)
        elif self.is_red_pixel(x, y):
            r00 = float(self.get_pixel(x - 1, y - 1))
            r01 = float(self.get_pixel(x + 1, y - 1))
            r10 = float(self.get_pixel(x - 1, y + 1))
            r11 = float(self.get_pixel(x + 1, y + 1))
            return int(round(self.__bilinear_interp(r00, r01, r10, r11, 0.5, 0.5)))
        elif not y % 2 == 0 and x % 2 == 0: # Between blue pixels horizontally
            r0 = float(self.get_pixel(x - 1, y))
            r1 = float(self.get_pixel(x + 1, y))
            return int(round(self.__linear_interp(r0, r1, .5)))
        elif y % 2 == 0 and  not x % 2 == 0: # Between blue pixels vertically
            r0 = float(self.get_pixel(x, y - 1))
            r1 = float(self.get_pixel(x, y + 1))
            return int(round(self.__linear_interp(r0, r1, .5)))
        else:
            return 0


class DestImage:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.img = Image.new("RGB", (width, height), "white")
        self.data = self.img.getdata()

    def set_pixel(self, x, y, r, g, b):
        if x < 0 or x >= self.width:
            raise Exception()
        elif y < 0 or y >= self.height:
            raise Exception()

        self.data.putpixel((x, y), (r, g, b, 255))

    def save(self, save_to):
        self.img.save(save_to)

    def show(self):
        self.img.show()


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print "Invalid parameters"
        sys.exit(1)

    input_image = sys.argv[1]
    output_image = sys.argv[2]

    if not os.path.exists(input_image):
        print "Cannot find specified image '%s'"%input_image
        sys.exit(2)

    src = SourceImage(input_image)

    width = src.width
    height = src.height

    dest = DestImage(width, height)

    for y in range(0, height):
        for x in range(0, width):

            r = src.get_red(x, y)
            g = src.get_green(x, y)
            b = src.get_blue(x, y)
            dest.set_pixel(x, y, r, g, b)

    dest.save(output_image)
    dest.show()