import folium
from folium.plugins import Draw, MarkerCluster, MeasureControl, MiniMap, MousePosition
from geopy.geocoders import Nominatim
import geocoder

# initialize a Nomination object
Locator = Nominatim(user_agent="SitePlan")

def find_my_address():
    mylocation = geocoder.ip('me')
    #my latitude and longitude coordinates
    latitude= mylocation.geojson['features'][0]['properties']['lat']
    longitude = mylocation.geojson['features'][0]['properties']['lng']

    #get the location
    location = Locator.reverse(f"{latitude}, {longitude}")
    print("Your Current IP location is", location)


def find_address_coord():
    address = "111 Marlinway OldHarbourGlade Jamaica W.I."

    #get the location detail 
    location = Locator.geocode(address)

    print("You find for the location:", location)
    print(f"The Latitude of {location} is: <{location.latitude}>")
    print(f"The Longitude of {location} is: <{location.longitude}>")


def mapper():
    # define map coordinates
    coords = [18.039, -77.509]
    formatter = "function(num) {return L.Util.formatNum(num, 3) + ' &deg; ';};"

    # Display map
    site_map = folium.Map(location=coords, width=750, height=500, zoom_start=16)
    # add marker
    folium.Marker(coords, popup = 'Building Site Location').add_to(site_map)
    site_map.add_child(MeasureControl())
    Draw(export=True).add_to(site_map)
    MousePosition(
        position="topright",
        separator=" | ",
        empty_string="NaN",
        lat_first=True,
        num_digits=20,
        prefix="Coordinates:",
        lat_formatter=formatter,
        lng_formatter=formatter,
    ).add_to(site_map)
    MiniMap(
        #tile_layer="Cartodb dark_matter",
        toggle_display=True,
        zoom_level_offset=-2,

        ).add_to(site_map)


    # show
    site_map.show_in_browser()

mapper()
