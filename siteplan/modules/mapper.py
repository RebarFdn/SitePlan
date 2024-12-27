import io
import os
from pathlib import Path
import folium
from folium.plugins import Draw, MarkerCluster, MeasureControl, MiniMap, MousePosition
from hex_htmltoimg import generate_image_from_html

from PIL import Image
from config import BASE_PATH, MAPS_PATH

def enshure_maps_dir(dir_path:Path)->None:
    """Checks if a directory exists, if not creates it.

    Args:
        dir_path (str): path to the required directory to validate
    """
    
    if dir_path.exists:
        pass
    else:
        dir_path.mkdir()
    return 

enshure_maps_dir(dir_path=MAPS_PATH)


class Mapper:
    formatter = "function(num) {return L.Util.formatNum(num, 3) + ' &deg; ';};"

    def __init__(self, coords:list=None, marker:bool=False, circle_marker:bool=True, mouse_pos:bool=False, 
                draw:bool=False, minimap:bool=False,  measurement:bool=False, width:int=480, height:int=440,
                zoom:int=15 ):
        self.coords = coords
        self.width = width
        self.height = height
        self.map =  folium.Map(location=coords, width=width, height=height,  zoom_start=zoom)
        self.add_marker(signal=marker)
        self.add_mouse_position(signal=mouse_pos)
        self.add_draw_tools(signal=draw)
        self.add_minimap(signal=minimap)
        self.add_measure_controll(signal=measurement)  
        self.circle_marker(signal=circle_marker)
        self.clear_img_cache()      


    def add_marker(self, signal:bool):
        if signal:
            # add marker
            folium.Marker(self.coords, popup = 'Building Site Location').add_to(self.map)

    
    def circle_marker(self, signal:bool):
        radius = 50
        folium.CircleMarker(
            location=self.coords,
            radius=radius,
            color="cornflowerblue",
            stroke=False,
            fill=True,
            fill_opacity=0.3,
            opacity=1,
            popup="{} pixels".format(radius),
            tooltip=f"Site Location {self.coords}",
        ).add_to(self.map)
        

    def add_mouse_position(self, signal:bool):
        if signal:
            MousePosition(
                position="topright",
                separator=" | ",
                empty_string="NaN",
                lat_first=True,
                num_digits=20,
                prefix="Coordinates:",
                lat_formatter=self.formatter,
                lng_formatter=self.formatter,
            ).add_to(self.map)


    def add_draw_tools(self, signal:bool):
        if signal:
            Draw(export=True).add_to(self.map)

    def add_measure_controll(self, signal:bool):
        if signal:
            self.map.add_child(MeasureControl())

    
    def add_minimap(self, signal:bool):
        if signal:
            MiniMap(
            #tile_layer="Cartodb dark_matter",
            toggle_display=True,
            zoom_level_offset=-2,

            ).add_to(self.map)

    @property
    def show_map(self):
        self.map.show_in_browser()

    def clear_img_cache(self):
        files = BASE_PATH.glob('*.jpg')
        if files:
            for file in files:
                print(file)
                os.remove(file)
        
    
    def save_map(self, handle:str)->Path:   
        """Saves the map as a html file to the maps directory"""     
        map_path:Path = MAPS_PATH / f"{handle}.html"        
        self.map.save(map_path) 
        return map_path
    
    
    def save_map_image(self, handle:str)->Path:
        """Saves the map as a png image file to the maps directory""" 
        map_path:Path = MAPS_PATH / f"{handle}.html"
        map_image_path:Path = MAPS_PATH / f"{handle}.png"
        
        if map_path.exists():
            replacements = {
                '{{title}}': 'Location Map',
                '{{content}}': 'Image Generated from Html !'
            }
            img_file = generate_image_from_html(
                map_path,                
                map_image_path,
                replacements,
                width=self.width,
                height=self.height
            )
            
            return img_file
        return None



    
    


   
    
    





