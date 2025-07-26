from .tokens import x_bogus, x_gnarly
from urllib.parse import urlencode

params = {
    "aid": "1988",
    "app_language": "uk-UA",
    "app_name": "tiktok_web",
    "browser_language": "uk-UA",
    "browser_online": "true",
    "browser_platform": "Linux x86_64",
    "channel": "tiktok_web",
    "cookie_enabled": "true",
    "coverFormat": "2",
    "data_collection_enabled": "false",
    "device_platform": "web_pc",
    "focus_state": "true",
    "from_page": "music",
    "is_fullscreen": "false",
    "is_page_visible": "true",
    "language": "uk-UA",
    "os": "linux",
    "region": "UA",
    "screen_height": "1080",
    "screen_width": "1920",
    "tz_name": "Europe/Kiev",
    "user_is_login": "false",
    "webcast_language": "uk-UA"
}

async def main(client, id: int, cursor: int=0, count: int=1) -> dict:
    params['musicID'] = id
    params['count'] = count
    params['cursor'] = cursor
    for key in client.params: params[key] = client.params[key]

    url = f"https://www.tiktok.com/api/music/item_list/?{urlencode(params)}"
    client_user_agent = client.session.headers["User-Agent"]

    bogus = x_bogus.create(url, client_user_agent)
    gnarly = x_gnarly.create(url, client_user_agent)
    url += f"&X-Bogus={bogus}&X-Gnarly={gnarly}"

    headers = {'User-Agent': client_user_agent, 'Accept-Encoding': 'gzip, deflate', 'Accept': '*/*', 'Connection': 'keep-alive'}

    response = await client.session.get(url, headers=headers, follow_redirects=True)
    return response.json()