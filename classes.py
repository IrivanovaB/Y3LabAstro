import numpy as np

class Frame:
    """
    Parent class for anything that can constitute a layer.

    Inputs
        data : numpy array
            the image data (or layer data)
        shape : tuple
            shape of the image data (i.e. dimensions of image)
    """
    def __init__(self, data):
        self.data = data
        self.__shape__ = np.shape(data)

    def shape(self):
        return self.__shape__

class Image(Frame):
    """
    Child class of Frame. Functions as representing an image layer. 
    """
    def __init__(self, data):
        super().__init__(data)
        self.__original__ = data

    def original(self):
        return self.__original__

class Mask(Frame):
    """
    Child class of Frame. Functions as a mask overtop of an image.
    """
    def __init__(self, data):
        super().__init__(data)