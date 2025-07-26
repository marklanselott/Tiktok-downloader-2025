from random_user_agent.params import OperatingSystem
from random_user_agent.user_agent import UserAgent
from dataclasses import dataclass, field
from .content import video, music, photo
from httpx import AsyncClient
from bs4 import BeautifulSoup
from enum import Enum
import json

class TypesEnum(Enum):
    VIDEO = "video"
    MUSIC = "music"
    PHOTO = "photo"

types = {t.value: t for t in TypesEnum}
funcs = {TypesEnum.VIDEO: video.main,TypesEnum.MUSIC: music.main, TypesEnum.PHOTO: photo.main}

random_user_agent = UserAgent(operating_systems=[OperatingSystem.WINDOWS.value]).get_random_user_agent

@dataclass
class Browser:
    name: str | None = None
    version: str | None = None
    
    def __init__(self, string: str = None):
        if self.name is None or self.version is None:
            if string is None: string = random_user_agent()

        self.user_agent_string = string
        parts = string.split("/", 1)
        if len(parts) >= 2: self.name = parts[0]; self.version = parts[1]
        else: self.name = string; self.version = ""

    @property
    def user_agent(self) -> str: return self.user_agent_string

@dataclass
class Client:
    session: AsyncClient
    browser: Browser = field(default_factory=lambda: Browser(random_user_agent()))
    params: dict = field(default_factory=dict)

    def __post_init__(self):
        self.session.headers.update({
            'User-Agent': self.browser.user_agent, 
            'Referer': 'https://www.tiktok.com/'
        })

    def update_params(self, data: dict):
        WebIdLastTime = data["webapp.app-context"]["webIdCreatedTime"]
        device_id = data["webapp.app-context"]["wid"]
        odinId = data["webapp.app-context"]["odinId"]
        clientABVersions = list(map(int, (data["webapp.app-context"]["abTestVersion"]["versionName"]).split(",")))
        
        self.params = {
            "webIdLastTime": WebIdLastTime,
            "device_id": device_id,
            "odinId": odinId,
            "clientABVersions": clientABVersions,
            "browser_name": self.browser.name,
            "browser_version": self.browser.version
        }

    async def get_type(self, url: str) -> TypesEnum:
        def search_type(url: str) -> str | None:
            for t in types.keys():
                if types[t].value in url:
                    return types[t]

        def search_id(url: str) -> str | None:
            return url.split("?")[0].split("/")[-1].split("-")[-1]

        if self.params == {}:
            response = await self.session.get(url, follow_redirects=True)
            self.session.cookies.update(response.cookies)

            soup = BeautifulSoup(response.text, 'html.parser')


            if universal_data := soup.find("script", id="__UNIVERSAL_DATA_FOR_REHYDRATION__"):
                self.update_params(json.loads(universal_data.string)['__DEFAULT_SCOPE__'])
        
        if type := search_type(url):
            return type, search_id(url)
        else:
            response = await self.session.head(url, follow_redirects=True)

            location = response.url
            if location: return search_type(str(location)), search_id(str(location))

            else: raise ValueError("Get type failed, no Location header found.")

    async def get_data(self, type: TypesEnum, id: str) -> dict:
        return await funcs[type](self, id)