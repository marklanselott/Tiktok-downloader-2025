from urllib.parse import urlencode
from aiohttp import ClientSession
from pydantic import BaseModel
from bs4 import BeautifulSoup
import json, execjs, requests


class Browser(BaseModel):
    name: str
    version: str


class Client:
    def __init__(self, browser: Browser, proxy: str=None, xbogus_path: str='./TikTok/xbogus'):
        self.browser = browser
        self.proxy = proxy
        self.headers = {"user-agent": f"{browser.name}/{browser.version}"}
        self.history_len: int = 0
        self.WebIdLastTime: int = None
        self.clientABVersions: list[int] = []
        self.odinId = None
        self.device_id = None
        self.session = None
        self.code = execjs.compile(f"""const xbogus = require('{xbogus_path}');""")

    def update_client(self, universal_data: dict):
        self.WebIdLastTime = universal_data["__DEFAULT_SCOPE__"]["webapp.app-context"]["webIdCreatedTime"]
        self.device_id = universal_data["__DEFAULT_SCOPE__"]["webapp.app-context"]["wid"]
        self.odinId = universal_data["__DEFAULT_SCOPE__"]["webapp.app-context"]["odinId"]
        self.clientABVersions = list(map(int, (universal_data["__DEFAULT_SCOPE__"]["webapp.app-context"]["abTestVersion"]["versionName"]).split(",")))

    async def get_item_id(self, url: str):
        item_id = None

        location = None

        if len(url) > 40: location = url
        else:
            try:
                async with self.session.head(url) as response:
                    if "location" in response.headers:
                        location = response.headers.get("location")
            except:
                async with self.session.get(url) as response:
                    html = await response.text()
                    soup = BeautifulSoup(html, "html.parser")
                    universal_data = soup.find("script", id="__UNIVERSAL_DATA_FOR_REHYDRATION__")

                    self.update_client(universal_data)

                    if universal_data == None: print("Not find universal_data(")
                    else: universal_data = json.loads(universal_data.string)

                    try: location = universal_data['__DEFAULT_SCOPE__']['seo.abtest']['canonical']
                    except: pass

        if location != None:
            path = location.split("?")[0].split("/")
            item_id = path[-1].split("-")[-1].split(".")[0]
        
            return item_id
        
        else: raise ValueError("Not found location(")

    async def get_item(self, itemId: int) -> dict:
        url = "https://www.tiktok.com/api/item/detail/"

        params = {
            'WebIdLastTime': self.WebIdLastTime, 
            'aid': '1988', 
            'app_language': 'uk-UA', 
            'app_name': 'tiktok_web', 
            'browser_language': 'uk-UA', 
            'browser_name': self.browser.name, 
            'browser_online': 'true', 
            'browser_platform': 'Win32', 
            'browser_version': self.browser.version, 
            'channel': 'tiktok_web', 
            'clientABVersions': self.clientABVersions, 
            'cookie_enabled': 'true', 
            'coverFormat': '2', 
            'data_collection_enabled': 'true', 
            'device_id': self.device_id, 
            'device_platform': 'web_pc', 
            'focus_state': 'true', 
            'from_page': 'user', 
            'history_len': self.history_len, 
            'is_fullscreen': 'false', 
            'is_page_visible': 'true', 
            'itemId': itemId, 
            'language': 'uk-UA', 
            'odinId': self.odinId, 
            'os': 'windows', 
            'priority_region': 'UA', 
            'region': 'UA', 
            'screen_height': '1080', 
            'screen_width': '1920', 
            'tz_name': 'Europe/Kiev', 
            'user_is_login': 'true', 
            'webcast_language': 'uk-UA'
        }
    
        params['X-Bogus'] = self.xbogus(f"{url}?{urlencode(params)}", self.headers['user-agent'])

        response = requests.get(
            f"{url}?{urlencode(params)}", 
            headers=self.headers
        ).json()

        self.history_len += 1

        return response

    async def start(self):
        self.session = ClientSession(proxy=self.proxy, headers=self.headers)

        async with self.session.get("https://www.tiktok.com/", proxy=self.proxy) as response:
            html = await response.text()
            soup = BeautifulSoup(html, "html.parser")
            universal_data = soup.find("script", id="__UNIVERSAL_DATA_FOR_REHYDRATION__")

            if universal_data == None: raise ValueError("Not find universal_data(")
            else: universal_data = json.loads(universal_data.string)

            self.update_client(universal_data)

    async def close(self):
        if self.session != None:
            await self.session.close()

    def xbogus(self, url: str, user_agent: str) -> str:
        result = self.code.call("xbogus", url, user_agent)
        return result

