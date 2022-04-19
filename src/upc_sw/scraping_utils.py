import pandas as pd
import geopandas as gpd
import requests
from tqdm import tqdm

import upcp.scrapers.ams_bgt_scraper as ams_bgt_scraper
import upcp.utils.las_utils as las_utils
import upc_sw.poly_utils as poly_utils


CRS = 'epsg:28992'

BGT_use_columns = ['geometry', 'identificatie_lokaalid', 'naam']
BGT_namedict = {'BGT': 'bgt_functie',
                'BGTPLUS': 'plus_type'}

TERRAS_WFS_URL = 'https://api.data.amsterdam.nl/v1/wfs/horeca/?'
TERRAS_use_columns = ['geometry', 'zaaknummer', 'naam']


def get_terras_data_for_bbox(bbox, layers=None):
    """Scrape 'terras' data in a given bounding box."""
    gdf = gpd.GeoDataFrame(columns=TERRAS_use_columns, crs=CRS)
    gdf.index.name = 'id'

    params = 'REQUEST=GetFeature&' \
             'SERVICE=WFS&' \
             'VERSION=2.0.0&' \
             'TYPENAMES=exploitatievergunning-terrasgeometrie&'

    if bbox is not None:
        bbox_string = str(bbox[0][0]) + ',' + str(bbox[0][1]) + ',' \
                      + str(bbox[1][0]) + ',' + str(bbox[1][1])
        params = params + 'BBOX=' + bbox_string + '&'

    params = params + 'OUTPUTFORMAT=geojson'

    response = requests.get(TERRAS_WFS_URL + params)
    try:
        json = response.json()
        if json['numberReturned'] > 0:
            gdf = gpd.GeoDataFrame.from_features(
                                    response.json(), crs=CRS).set_index('id')
            gdf['naam'] = 'terras'
            gdf['geometry'] = gdf['geometry'].apply(poly_utils.fix_invalid)
            return gdf[TERRAS_use_columns]
        else:
            return gdf
    except ValueError:
        return gdf


def get_bgt_data_for_bbox(bbox, layers):
    """Scrape BGT data in a given bounding box."""
    gdf = gpd.GeoDataFrame(columns=BGT_use_columns, crs=CRS)
    gdf.index.name = 'ogc_fid'

    content = []
    for layer in layers:
        # Scrape data from the Amsterdam WFS, this will return a json response.
        json_content = ams_bgt_scraper.scrape_amsterdam_bgt(layer, bbox=bbox)

        layer_type = BGT_namedict[layer.split('_')[0]]

        # Parse the downloaded json response.
        if json_content is not None:
            gdf = gpd.GeoDataFrame.from_features(
                                json_content, crs=CRS).set_index('ogc_fid')
            gdf = gdf[gdf['bgt_status'] == 'bestaand']
            gdf['naam'] = gdf[layer_type]
            content.append(gdf[BGT_use_columns])

    if len(content) > 0:
        gdf = pd.concat(content)
    return gdf


def process_tiles(tiles, bgt_layers, scraper=get_bgt_data_for_bbox):
    """This method scrapes data precisely for the needed area."""
    bgt_data = []

    tile_tqdm = tqdm(tiles, unit='tile', smoothing=0)
    for tilecode in tile_tqdm:
        tile_tqdm.set_postfix_str(tilecode)

        bbox = las_utils.get_bbox_from_tile_code(tilecode, padding=0)
        bgt_data.append(scraper(bbox, bgt_layers))

    bgt_gdf = pd.concat(bgt_data)
    return bgt_gdf[~bgt_gdf.duplicated()]


def process_folder(folder, bgt_layers, scraper=get_bgt_data_for_bbox):
    """
    This method scrapes all data in an area defined as the bounding box for all
    point cloud tiles  in a given folder. This results in some unnecessary
    data, but is much faster if the folder  contains many files, and / or is
    densily packed within the bounding box.
    """
    bbox = las_utils.get_bbox_from_las_folder(folder, padding=0)
    bgt_data = scraper(bbox, bgt_layers)
    return bgt_data
