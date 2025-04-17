from TikTok import Client, Browser
import asyncio, aiofiles, json

client = Client(Browser(name='Mozilla', version='5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36'))


async def download_video(client: Client, url: str, path: str):
    async with client.session.get(url) as response:
        async with aiofiles.open(path, 'wb') as f:
            await f.write(await response.read())
        print(f"Video downloaded to {path}")



async def main():
    await client.start()
    id = await client.get_item_id("https://vm.tiktok.com/ZMBPRbRkT/")
    item = await client.get_item(id)
    
    # json.dump(item, open(".json", "w", encoding="utf-8"), indent=4, ensure_ascii=False)

    await download_video(client, item['itemInfo']['itemStruct']['video']['playAddr'], f"video_{id}.mp4")

    await client.close()

asyncio.run(main())