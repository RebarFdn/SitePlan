# image processor
import glob, os
from PIL import Image, ImageFilter, ImageOps
from io import BytesIO
from time import sleep
from pydantic import BaseModel
from collections import ChainMap
from config import DROPBOX_PATH

image_filter = {
    'blur': ImageFilter.BLUR,
    'contour': ImageFilter.CONTOUR, 
    'detail': ImageFilter.DETAIL, 
    'eh': ImageFilter.EDGE_ENHANCE, 
    'ehm': ImageFilter.EDGE_ENHANCE_MORE, 
    'emboss': ImageFilter.EMBOSS, 
    'fe': ImageFilter.FIND_EDGES,
    'sm': ImageFilter.SMOOTH, 
    'smm': ImageFilter.SMOOTH_MORE, 
    'shp': ImageFilter.SHARPEN
}


class ImageManager(BaseModel):
    jpgs:list = glob.glob(f"{DROPBOX_PATH}/**/*.jpg", recursive=True)
    pngs: list = glob.glob(f"{DROPBOX_PATH}/**/*.png", recursive=True)

    @property
    def image_index(self):
        return list(ChainMap(self.jpgs, self.pngs))

    def display_index(self, index:int=0 ):        
        if self.image_index:
            if index > self.image_index.__len__() - 1 :
                print(f'select a index less than {self.image_index.__len__()} but no negative numbers.')
            else:
                img = Image.open(self.image_index[index])
                imout = img.filter(image_filter['detail'])
                #img.show()
                mmg = ImageOps.mirror(imout)
                poster = ImageOps.posterize(imout, 8)
                imout.show()
                mmg.show()
                poster.show()
                sleep(5)
                img.close()


            

iman = ImageManager()

iman.display_index(index=1)

