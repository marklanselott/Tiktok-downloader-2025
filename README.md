```python
from TikTok.client import Client
from httpx import AsyncClient
import asyncio, json


async def download_video(url: str, client: Client):
    response = await client.session.get(url)
    with open("video.mp4", "wb") as f:
        f.write(response.content)


async def main():
    url = "https://vm.tiktok.com/ZMBdEeFgm"

    client = Client(session=AsyncClient())
    type, id = await client.get_type(url)
    data = await client.get_data(type, id)

    json.dump(
        data, 
        open("data.json", "w", encoding="utf-8"), 
        ensure_ascii=False, 
        indent=4
    )

    await download_video(data['itemInfo']['itemStruct']['video']['playAddr'], client)

asyncio.run(main())
```
