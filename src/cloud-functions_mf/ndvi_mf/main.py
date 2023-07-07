import json
import ee
from datetime import datetime
import calendar
import geojson
import shapely
from google.auth import compute_engine
from shapely import wkt

scopes = ["https://www.googleapis.com/auth/earthengine"]
credentials = compute_engine.Credentials(scopes=scopes)
ee.Initialize(credentials)


def get_ndvi_month(request):

      request_json = request.get_json(silent=True)
      print('Req Json',type(request_json))
      replies = []
      calls = request_json['calls']
      for call in calls:

        farm_json_str = call[0]
        #farm_name = call[1]
        farm_year = call[1]
        farm_mon = call[2]
        farm_json = shapely.wkt.loads(farm_json_str)
        farm_poly = geojson.Feature(geometry=farm_json, properties={})
        farm_aoi = ee.Geometry(farm_poly.geometry)

        #print("Farm ",farm_name)

        ee_ndvi = farm_ndvi_calc(farm_aoi,farm_year,farm_mon)
        #ndvi = ee_ndvi.getInfo()

        replies.append(ee_ndvi)
      return json.dumps({'replies': [str(x) for x in ee.List(replies).getInfo()]})

def farm_ndvi_calc(farm_aoi, year, month):
    first, last = calendar.monthrange(year, month)
    first_date = datetime(year, month, 1)
    startDate = first_date.strftime("%Y-%m-%d")
    last_date = datetime(year, month, last)
    endDate = last_date.strftime("%Y-%m-%d")
    sentinel2 = ee.ImageCollection("COPERNICUS/S2_SR")
    filtered = sentinel2.filter(ee.Filter.date(startDate, endDate))
    composite = filtered.filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20)).median()
    ndviImage = composite.normalizedDifference(['B5', 'B4']).rename('NDVI')
    ndviValue = ndviImage.reduceRegion(**{
        'geometry': farm_aoi,
        'reducer': ee.Reducer.median(),
        'scale': 10
    }).get('NDVI');
    return ndviValue
