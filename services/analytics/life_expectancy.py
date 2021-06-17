from flask import Blueprint, jsonify, request
import pandas as pd
import geopandas as gpd
import pysal as ps
import networkx as nx
import folium
from folium.plugins import MarkerCluster
import os
import pickle

def cached(cachefile):
    """
    A function that creates a decorator which will use "cachefile" for caching the results of the decorated function "fn".
    """
    def decorator(fn):  # define a decorator for a function "fn"
        def wrapped(*args, **kwargs):   # define a wrapper that will finally call "fn" with all arguments            
            # if cache exists -> load it and return its content
            if os.path.exists(cachefile):
                    with open(cachefile, 'rb') as cachehandle:
                        print("using cached result from '%s'" % cachefile)
                        return pickle.load(cachehandle)

            # execute the function with all arguments passed
            res = fn(*args, **kwargs)

            # write to cache file
            with open(cachefile, 'wb') as cachehandle:
                print("saving result to cache '%s'" % cachefile)
                pickle.dump(res, cachehandle)

            return res

        return wrapped

    return decorator   # return this "customized" decorator that uses "cachefile"

@cached('tracts_disparity.pickle')
def load_data():
    lfe = pd.read_csv('data/US_A.CSV')[['Tract ID', 'e(0)']] \
        .rename(index=str, 
                columns={'Tract ID': 'GEOID', 
                        'e(0)':'life_expectancy'})
    lfe['GEOID'] = lfe['GEOID'].astype(str)
    gdf = gpd.read_file('data/geo/tracts/usa_tracts.shp')[['GEOID','geometry']]
    gdf = gdf.merge(lfe).set_index('GEOID')

    swm = ps.weights.Rook.from_dataframe(gdf)
    tract_to_neighbors = swm.neighbors

    fips_to_lfe = dict(zip(lfe['GEOID'].astype(str), lfe['life_expectancy']))

    g = nx.Graph()
    g.add_nodes_from(gdf.index)

    for tract, neighbors in tract_to_neighbors.items():
        avail_tracts = fips_to_lfe.keys()
        # some tracts don't seem to show up in the life expectancy dataset
        # these may be tracts with no population
        if tract in avail_tracts:
            for neighbor in neighbors:
                if neighbor in avail_tracts:
                    tract_lfe = fips_to_lfe[tract]
                    neighbor_lfe = fips_to_lfe[neighbor]
                    disparity = abs(tract_lfe - neighbor_lfe)
                    g.add_edge(tract, neighbor, disparity=disparity)
        # remove the node from the graph if the node is not in the life
        # expectancy dataset
        elif tract in g.nodes:
            g.remove_node(tract)

    sorted_list = sorted(g.edges(data=True), key=lambda x: x[2]['disparity'], reverse=True)

    return lfe, sorted_list, gdf


life_expectancy = Blueprint('life_expectancy', __name__, template_folder='templates')

@life_expectancy.route('/folium')
# read config file and return json to the client!
def get_map():
    limit = request.args.get('limit')
    lfe, sorted_list, gdf = load_data()

    top_50 = sorted_list[:int(limit)]
    top_50_tracts = []
    for t in top_50:
        if t[0] not in top_50_tracts:
            top_50_tracts.append(t[0])
        if t[1] not in top_50_tracts:
            top_50_tracts.append(t[1])

    
    top_50_tracts_gdf = gdf[gdf.index.isin(top_50_tracts)].reset_index()[['GEOID', 'geometry', 'life_expectancy']]
    top_50_tracts_gdf.to_file('selected_tracts.geojson', driver='GeoJSON')


    m = folium.Map(tiles='cartodbpositron', min_zoom=4, zoom_start=4.25, 
               max_bounds=True,location=[33.8283459,-98.5794797],
               min_lat=5.499550, min_lon=-160.276413, 
               max_lat=83.162102, max_lon=-52.233040)
    marker_cluster = MarkerCluster(
        options = {'maxClusterRadius':15, 
                'disableCusteringAtZoom':5, 
                'singleMarkerMode':True}).add_to(m)
    folium.Choropleth(
        geo_data = 'selected_tracts.geojson',
        data = lfe,
        columns = ['GEOID','life_expectancy'],
        fill_color = 'YlGn',
        key_on = 'feature.properties.GEOID',
        name = 'geojson',
        legend_name='Life Expectancy'
    ).add_to(m)

    for i, tract in top_50_tracts_gdf.iterrows():
        x = tract.geometry.centroid.x
        y = tract.geometry.centroid.y
        l = tract.life_expectancy
        folium.CircleMarker([y, x], radius=8, color='black', 
                            fill_color='white', fill_opacity=0.5, 
                            tooltip='Life expectancy: {}'.format(str(l))).add_to(marker_cluster)
        
    f = folium.Figure()
    title = '<h2>Does your census tract determine how ' + \
            'long you will live?</h2>'
    subtitle = '<h4><i>Census tract neighbors across ' + \
            'the U.S. with the widest disparities ' + \
            'in life expectancy<i></h4>'
    f.html.add_child(folium.Element(title))
    f.html.add_child(folium.Element(subtitle))
    f.add_child(m)

    # not sure if this works
    # data = {'html': f.html}
    # if it does not, you can save the file and read it as text
    f.save("map.html")
    file = open("map.html", "r") 
    data = {'html': file.read()}
    
    return jsonify(data)
