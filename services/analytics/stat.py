import pandas as pd
import geopandas as gpd
import pysal as ps
import networkx as nx
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