import requests

__all__ = ['Geocode']


class Geocode(object):
    def __init__(self, location, apikey) -> None:
        super().__init__()
        self.location = location
        self.apikey = apikey

    def getGeocode(self):
        if self.location is None:
            return "No Location was provided"
        self.location = self.location.replace(" ", "+")
        URL = (
            f'https://maps.googleapis.com/maps/api/geocode/json?address={self.location}&key={self.apikey}')
        result = requests.get(URL).json()

        lat = result['results'][0]['geometry']['location']['lat']
        lon = result['results'][0]['geometry']['location']['lng']
        return lat, lon


if __name__ == '__main__':
    from pprint import pprint
    obj = Geocode('Kolkata', 'Insert-API-Key')
    pprint(obj.getGeocode(), indent=4)
