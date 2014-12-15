#!/usr/bin/python
# coding: utf8

import os
import unicodecsv
from lookup_table import feature_code, country_code
import fiona


class Geonames(object):
    def __init__(self, path):
        self.container = []
        self.load(path)

    def __repr__(self):
        return self.label

    @property
    def label(self):
        if self.container:
            country = self.container[0]['properties'].get('country')
        return '<Geonames - {0} [{1}]>'.format(country, len(self.container))

    def load(self, path):
        file_name = os.path.basename(path)
        with open(path) as f:
            fieldnames = [
                'geonameid',
                'name',
                'asciiname',
                'alternate',
                'y',
                'x',
                'feature_class',
                'feature_code',
                'country_code',
                'cc2',
                'admin1_code',
                'admin2_code',
                'admin3_code',
                'admin4_code',
                'population',
                'elevation',
                'dem',
                'timezone',
                'modification_date'
            ]

            reader = unicodecsv.DictReader(f, fieldnames=fieldnames, dialect='excel-tab', encoding='utf-8')

            for row in reader:
                # Main Lookup
                lookup_f_code = feature_code.get(row['feature_code'])
                lookup_country = country_code.get(row['country_code']) 

                # Derived Fields
                # Feature Class Lookup
                if lookup_f_code:
                    f_class = lookup_f_code.get('class')
                    f_code = lookup_f_code.get('name')
                    f_code_id = lookup_f_code.get('code')
                    summary = lookup_f_code.get('description')
                else:
                    f_class = ''
                    f_code = ''
                    f_code_id = ''
                    summary = ''

                # Country lookup
                if lookup_country:
                    continent = lookup_country.get('Continent')
                    country = lookup_country.get('Country')
                else:
                    continent = ''
                    country = ''
                self.country = country

                # Convert to Numbers
                x = float(row['x'])
                y = float(row['y'])

                # Make Numbers
                geonameid = int(row['geonameid'])
                population = row['population']
                if population:
                    population = int(row['population'])
                elevation = row['elevation']
                if elevation:
                    elevation = int(row['elevation'])
                else:
                    elevation = 0
                dem = row['dem']
                if dem:
                    dem = int(row['dem'])

                # Create GeoJSON Feature
                geometry = {
                    'type': 'Point',
                    'coordinates': [x, y]
                }
                properties = {
                    'geonameid': geonameid,
                    'name': row['name'],
                    'asciiname': row['asciiname'],
                    'alternate': row['alternate'],
                    'f_class': f_class,
                    'f_code': f_code,
                    'f_code_id': f_code_id,
                    'summary': summary,
                    'country': country,
                    'continent': continent,
                    'population': population,
                    'elevation': elevation,
                    'dem': dem,
                }
                feature = {
                    'geometry': geometry,
                    'properties': properties,
                }
                # Add the feature inside Container to retrieve later on when exporting
                self.container.append(feature)

    def export(self, path):
        folder, file_name = os.path.split(path)
        if folder:
            if not os.path.exists(folder):
                os.mkdir(folder)

        encoding = 'utf-8'
        crs = {'init':'epsg:4326'}
        driver = 'ESRI Shapefile'
        properties = [
            ('geonameid', 'int'),
            ('name', 'str'),
            ('asciiname', 'str'),
            ('alternate', 'str'),
            ('f_class', 'str'),
            ('f_code', 'str'),
            ('f_code_id', 'str'),
            ('summary', 'str'),
            ('country', 'str'),
            ('continent', 'str'),
            ('population', 'int'),
            ('elevation', 'int'),
            ('dem', 'int'),
        ]
        schema = {
            'geometry':'Point',
            'properties': properties
        }

        with fiona.open(
            path, 'w', 
            driver=driver, 
            schema=schema, 
            crs=crs, 
            encoding=encoding) as sink:
            for feature in self.container:
                sink.write(feature)

if __name__ == '__main__':
    geonames = Geonames('CA.txt')
    geonames.export('output/test.shp')