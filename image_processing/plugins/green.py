import os
import cv2
import numpy as np
from PIL import Image
from plugin import Plugin


class Green(Plugin):

    def __init__(self):
        pass

    def vegetation_from_file(self, image_path):
        """Read in image from file."""
        if not os.path.exists(image_path):
            return -1
        image = Image.open(image_path)
        image = np.array(image)
        return self.green(image)

    def write_masked_image(np_image, mask, dst='/tmp/x.png'):
        """debug: write out image with detected green as 255."""
        image = np.copy(np_image)
        image[:,:,1] = np.where(mask, 255, image[:,:,1])
        x = Image.fromarray(np.uint8(image))
        x.save(dst)

    def green(self, image):
        """Calculate foliage coverage for RGB image.

        The image is first converted to the L*a*b* colour space. Lab is better
        suited to image processing tasks since it is much more intuitive than 
        RGB. In Lab, the lightness of a pixel (L value) is seperated from the 
        colour (A and B values). A negative A value represents degrees of
        green, positive A, degrees of red. Negative B represents blue, while 
        positive B represents yellow. A colour can never be red _and_ green or
        yellow _and_ blue at the same time. Therefore the Lab colour space 
        provides a more intuitive seperability than RGB (where all values must 
        be adjusted to encode a colour.) Furthermore, since lightness value (L)
        is represented independently from colour, a 'green' value will be robust 
        to varying lighting conditions.

        Return:
            A float in the range [0, 1].
            Where 0 corresponds to 0% detected green in the image,
                  1 corresponds to 100% green image.     
        """ 
        # convert RGB ordered image to lab space
        lab = cv2.cvtColor(image, cv2.COLOR_RGB2LAB)
        # alpha value ( < 0 = green, > 0 = red).
        _, a, _ = cv2.split(lab)
        # rescale
        a = a-128.0

        # (-25, -15) based on tobacco plants.
        # < -5 is very relaxed!
        mask = (-30 < a) & (a < -5) 
        # ratio of green appearing in the image
        green = a[mask]
        cov = green.size/float(a.size) 
        
        return cov

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    import sys
    test_image = sys.argv[1] 
    g = Green()
    green = g.vegetation_from_file(test_image)
    print("{:.4f}".format(green))
