# -*- coding: utf-8 -*-

"""
Basic functionality to work with place data.
"""

from dfutil import load_csv


def from_csv(place_csv, placerelation_csv=None, placerelation_related_places_csv=None):
    """
    Loads place data from the given CSV files.

    Args:
        place_csv (str):
            name of the file containing place data
        placerelation_csv (str, optional)
            name of the file containing placerelation data
        placerelation_related_places_csv (str, optional)
            name of the file containing placerelation_related_places data

    Returns:
        pandas.DataFrame
    """
    places = load_csv(place_csv)
    if placerelation_csv and placerelation_related_places_csv:
        placerelations_from_csv(places, placerelation_csv, placerelation_related_places_csv)
    return places


def placerelations_from_csv(places, placerelation_csv, placerelation_related_places_csv):
    """
    Loads placerelation data to the given places data frame.
    WARNING: The function modifies the given dataframe!

    Args:
        places (pandas.DataFrame):
            data frame containing place data
        placerelation_csv (str)
            name of the file containing placerelation data
        placerelation_related_places_csv (str)
            name of the file containing placerelation_related_places data

    Returns:
        pandas.DataFrame
    """

    TYPES = {
        1: 'is_on_map',
        2: 'is_submap',
        3: 'land_borders',
        4: 'too_small_on_map'
    }

    placerelations = load_csv(placerelation_csv)
    related_places = load_csv(placerelation_related_places_csv)
    related_places_dict = {}
    placerelations_dict = {}
    for i, row in placerelations.iterrows():
        placerelations_dict[row['id']] = (row['place'], TYPES[row['type']])
    for i, row in related_places.iterrows():
        if row['place'] not in related_places_dict:
            related_places_dict[row['place']] = []
        related_places_dict[row['place']].append(placerelations_dict[row['placerelation']])
    places['relations'] = places['id'].map(lambda id: related_places_dict.get(id, []))
    return places
