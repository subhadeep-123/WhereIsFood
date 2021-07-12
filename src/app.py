import os
import uuid
import configparser
from flask_restful import Api, Resource
from flask import Flask, jsonify, request
import requests

# Local Imports
from geocode import *

# Setting Flask Parameters
app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = b"{\xd0\x16gznb=\x06\x81\x9ba\xa7\x0c\xc6\xf7"
app.config['JSON_SORT_KEYS'] = False
app.logger.setLevel(10)
api = Api(app)

# File Paths
CONFIGURATION_FILE_PATH = '../config/config.ini'

if not os.path.isfile(CONFIGURATION_FILE_PATH):
    print("""
    Change the .example.config.ini -> config.ini,
    and fill the empty spaces by your own API credentials.
    Get yours API Credentials
    FourSquare Places API - https://developer.foursquare.com/docs/places-api/
    Google Maps GeoCoading API - https://developers.google.com/maps/documentation/geocoding/overview
    """)
    raise FileNotFoundError('config.ini missing in config directory')

configs = configparser.ConfigParser()
configs.read(CONFIGURATION_FILE_PATH)

try:
    # FourSquare API Keys
    F4S_clientID = configs['FourquareAPIkeys']['clientid']
    F4S_clientecret = configs['FourquareAPIkeys']['clientsecret']

    # Google API Keys
    G_API_KEY = configs['GoogleAPIkey']['APIKey']
except Exception as err:
    print(err)


class Search(Resource):
    def get(self):
        # FourSquare API Endpoint
        URL = 'https://api.foursquare.com/v2/venues/explore'

        # Query Parameters
        cityname = request.args.get('cityname')
        mealtype = request.args.get('mealtype')

        # GeoCoading the location
        geo = Geocode(cityname, G_API_KEY)
        lat, lng = geo.getGeocode()
        lat_lng = str(lat) + ',' + str(lng)
        app.logger.debug(f'Geocoded Lat and Lon {lat}, {lng}')

        # Paramets for FourSquare API request
        params = dict(
            client_id=F4S_clientID,
            client_secret=F4S_clientecret,
            query=mealtype,
            ll=lat_lng,
            radius=10000,
            v='20210712',
            limit=20,
        )
        app.logger.warning(f'Params Dictionary - {params}')
        result = requests.get(URL, params=params).json()
        places = list()
        for i in result['response']['groups'][0]['items']:
            tempDict = dict(
                place_name=i['venue']['name'],
                place_address=', '.join(
                    i['venue']['location']['formattedAddress']),
                place_category=i['venue']['categories'][0]['name']
            )
            places.append(tempDict.copy())

        return jsonify(
            {
                'meta': result['meta'],
                'city': result['response']['headerFullLocation'],
                'totalResults': result['response']['totalResults'],
                'type': result['response']['groups'][0]['type'],
                'places': places
            },
            200
        )


class Index(Resource):
    def get(self):
        linksDict = dict(
            search='/api/v1.0/restuarnts?cityname=location_name&mealtype=meal_name_here'
        )

        return jsonify({
            'message': 'Welcome to the WhereIsFood Endpoint',
            'status_code': 200,
            'request_id': str(uuid.uuid4()),
            'links': linksDict
        })


def main():
    """Set the URL paths of flask_restful"""
    api.add_resource(Index,
                     "/")
    api.add_resource(Search,
                     "/api/v1.0/restuarnts")

    app.run()


if __name__ == '__main__':
    main()
