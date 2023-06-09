import asyncio
from aiohttp import ClientSession
from pytile import async_login
import os
from os.path import join, dirname
from dotenv import load_dotenv
from requests_oauthlib import OAuth1Session
import requests
import json
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s:%(name)s - %(message)s")
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

class ClientSessionHandler:
    """last_timestamp: datetime | None = None
        latitude: float | None = None
        longitude: float | None = None
        uuid: str = "'b07ca79b131d71a4'"
    """
    def __init__(self):
        self.email = os.environ.get("EMAIL")
        self.password = os.environ.get("PASSWORD")
        self.target_uuid = 'b07ca79b131d71a4'
        self.target_locate = {"latitude": None, "longitude": None}
        print("Initializing session handler...")

    async def start_session(self) -> None:
        # Run
        print("Starting session handler...")
        async with ClientSession() as session:
            print("Starting session...")
            api = await async_login(self.email, 
                                    self.password,
                                    session)
            print(f"Session started!: {api}")
            tiles = await api.async_get_tiles()  # get all tiles
            for tile_uuid, tile in tiles.items():
                if tile_uuid == self.target_uuid:
                    print(f"The Tile's name is {tile.name}")
                    print(f"{tile.as_dict()}")
                    self.target_locate["latitude"] = tile.latitude
                    self.target_locate["longitude"] = tile.longitude
    
    def get_location(self) -> tuple:
        return (self.target_locate["latitude"], self.target_locate["longitude"])

                
                

class RequestsOauth1SessionHandler:
    def __init__(self):
        self.consumer_key = os.environ.get("CONSUMER_KEY")
        self.consumer_secret_key = os.environ.get("CONSUMER_SECRET_KEY")
        self.access_token = os.environ.get("ACCESS_TOKEN")
        self.access_token_secret = os.environ.get("ACCESS_TOKEN_SECRET")
        print("Initializing session handler...")
        
    def start_session(self) -> None:
        # Run
        print("Starting session handler...")
        oauth = OAuth1Session(self.consumer_key,
                              self.consumer_secret_key,
                              self.access_token,
                              self.access_token_secret)
        tweet_content = "Check, 1 2 3"
        payload = {"text": tweet_content}
        response = oauth.post("https://api.twitter.com/2/tweets", json=payload)
        if response.status_code == 201:
            logging.info("Tweet posted successfully!")
        else:
            raise Exception(
                f"Request failed: {response.status_code} {response.text}"
                )
        

class GmapsSessionHandler:
    """ &markers=color:blue %7C label:S %7C 62.107733,-145.541936
        &markers=size:tiny %7C color:green %7C Delta+Junction,AK
        &markers=size:mid %7C color:0xFFFF00 %7C label:C %7C Tok,AK
    """
    def __init__(self):
        self.api_key = os.environ.get("GOOGLE_MAPS_API_KEY")
        self.base_url = "https://maps.googleapis.com/maps/api/staticmap?"
        self.lat, self.lng = None, None
        print(type(self.api_key))
        print("Initializing Gmasps Seeson handler...")

    def start_session(self) -> None:
        LOCATE = (self._get_location())
        LOCATE = str(LOCATE[0]) + "," + str(LOCATE[1])
        ZOOM = 18
        MARKER = f"color:red%7C{LOCATE}"
        
        URL = self.base_url + "center=" + LOCATE + "&zoom=" + str(ZOOM) + "&size=1200x1200&markers=" + MARKER + "&key=" + self.api_key
        response = requests.get(URL)  # get request
        with open(f"maps.png", "wb") as file:
            if response.status_code != 200:
                raise Exception(f"Failed to download image: {response.status_code} {response.text}")
            file.write(response.content)
            print("Image successfully Downloaded: ", "map.png")
            
    def set_location(self, location: tuple) -> None:
        self.lat, self.lng = location
        
    def _get_location(self) -> tuple:
        if self.lat is None or self.lng is None:
            raise Exception("Location has not been set yet!")
        else:
            return self.lat, self.lng
        


def main():
    tile_handler = ClientSessionHandler()
    asyncio.run(tile_handler.start_session())
    location = tile_handler.get_location()
    logging.info(f"Location: {location}")
    # text_handler = RequestsOauth1SessionHandler()
    # text_handler.start_session()
    gmaps_handler = GmapsSessionHandler()
    gmaps_handler.set_location(location)
    gmaps_handler.start_session()
    
if "__main__" == __name__:
    main()
