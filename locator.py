import httpx
import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class Location:
    country: str
    lat: Optional[float] = None
    long: Optional[float] = None


username = os.getenv('GEOIP_ID')
if not username:
    raise ValueError("GEOIP_ID environment variable not set")
password = os.getenv('GEOIP_PASSWORD')
if not password:
    raise ValueError("GEOIP_PASSWORD environment variable not set")
auth = httpx.BasicAuth(username=username, password=password)
client = httpx.Client(auth=auth)
def locate(ip: str) -> Location | None:
    try:
        country = client.get(f'https://geolite.info/geoip/v2.1/country/{ip}')
        country.raise_for_status()
        country: str = country.json()["country"]["names"]["en"]
    except (httpx.HTTPError, KeyError, TypeError):
        return None
    try:
        city = client.get(f'https://geolite.info/geoip/v2.1/city/{ip}')
        city.raise_for_status()
        city: dict = city.json()
        loc = (city["location"]["latitude"], city["location"]["longitude"])
    except (httpx.HTTPError, KeyError, TypeError):
        loc = (None, None)
    return Location(country=country, lat=loc[0], long=loc[1])
