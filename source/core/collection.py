import os
import cv2
import copy
import PIL.Image
import numpy as np


class ImgBBox:
    def __init__(self, xmin, ymin, xmax, ymax, label):
        self.xmin = xmin
        self.ymin = ymin
        self.xmax = xmax
        self.ymax = ymax
        self.label = label


class ImgElement:
    def __init__(self, img, imgpath, label=None):
        self.img = img
        self.imgpath = imgpath
        self.label = label
        self.bboxes = []

    def add_bbox(self, xmin, ymin, xmax, ymax, label):
        self.bboxes.append(ImgBBox(xmin, ymin, xmax, ymax, label))

    def __repr__(self):
        return self.imgpath

    def __str__(self):
        return self.imgpath

    @property
    def height(self):
        return self.img.shape[0]

    @property
    def width(self):
        return self.img.shape[1]

    @property
    def img(self):
        return self.__img

    @img.setter
    def img(self, img):
        self.__img = img

    @property
    def imgpath(self):
        return self.__imgpath

    @imgpath.setter
    def imgpath(self, imgpath):
        self.__imgpath = imgpath

    @property
    def label(self):
        return self.__label

    @label.setter
    def label(self, label):
        self.__label = label

    @property
    def bboxes(self):
        return self.__bboxes

    @bboxes.setter
    def bboxes(self, bboxes):
        self.__bboxes = bboxes

    @classmethod
    def fromFile(cls, imgpath):
        img = cv2.imread(imgpath)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        return cls(img, imgpath)

    @classmethod
    def fromPILImage(cls, imgpil):
        img = np.array(imgpil)
        return cls(img, "")

    @classmethod
    def fromArray(cls, imgarr):
        img = copy.deepcopy(imgarr)   # FIXME: use np.copy?
        return cls(img, "")


class ImgCollectionBase:
    def __init__(self):
        self.collection = []

    def summary(self):
        return f"{self.__class__.__name__} contains {self.__len__()} images"

    def __len__(self):
        return 0


class ImgCollection(ImgCollectionBase):
    # TODO: auto-generate collection name

    def __init__(self):
        super(ImgCollection, self).__init__()
        self.collection = []

        # TODO: create a global config file for constants
        self.max_print_lines = 20   # FIXME: odd number will be rounded: 9 / 2 = 4

    def __repr__(self):
        return self.summary()

    def __str__(self):
        retstr = ""
        l = len(self.collection)
        if l <= self.max_print_lines:
            retstr += "".join([f"[{i}] {img}\n" for i, img in enumerate(self.collection)])
        elif self.max_print_lines > 0:
            h = self.max_print_lines // 2
            retstr += "".join([f"[{i}] {img}\n" for i, img in enumerate(self.collection[:h])])
            retstr += "......\n"
            retstr += "".join([f"[{l - h + i}] {img}\n" for i, img in enumerate(self.collection[-h:])])
        return retstr

    def __len__(self):
        return len(self.collection)

    def __getitem__(self, idx):
        if isinstance(idx, slice):
            return self.collection[idx.start:idx.stop:idx.step]
        return self.collection[idx]

    # TODO: does this also need slice?
    def __setitem__(self, idx, elem):
        self.collection[idx] = elem

    # FIXME: is this the standard/best way to implement the iterator?
    def __iter__(self):
        self.iter_idx = 0
        return self

    def __next__(self):
        if self.iter_idx < len(self.collection):
            x = self.collection[self.iter_idx]
            self.iter_idx += 1
            return x
        else:
            raise StopIteration

    def append(self, elem):
        self.collection.append(elem)

    def clear(self):
        self.collection = []
