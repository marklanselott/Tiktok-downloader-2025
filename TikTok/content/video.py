from urllib.parse import urlencode
from .tokens import x_bogus

params = {
    "aid": "1988", 
    "app_language": "uk-UA", 
    "app_name": "tiktok_web", 
    "browser_language": "uk-UA", 
    "browser_online": "true", 
    "browser_platform": "Win32", 
    "channel": "tiktok_web", 
    "cookie_enabled": "true", 
    "coverFormat": "2", 
    "data_collection_enabled": "true", 
    "device_platform": "web_pc", 
    "focus_state": "true", 
    "from_page": "user", 
    "is_fullscreen": "false", 
    "is_page_visible": "true", 
    "language": "uk-UA", 
    "os": "windows", 
    "priority_region": "UA", 
    "region": "UA", 
    "screen_height": "1080", 
    "screen_width": "1920", 
    "tz_name": "Europe/Kiev", 
    "user_is_login": "true", 
    "webcast_language": "uk-UA"
}

async def main(client, id: int) -> dict:
    params['itemId'] = id
    for key in client.params: params[key] = client.params[key]

    url = f"https://www.tiktok.com/api/item/detail/?{urlencode(params)}"

    token = x_bogus.create(url, client.browser.user_agent)
    url += f"&X-Bogus={token}"

    headers = {'User-Agent': client.browser.user_agent, 'Accept-Encoding': 'gzip, deflate', 'Accept': '*/*', 'Connection': 'keep-alive'}

    response = await client.session.get(url, headers=headers, follow_redirects=True)
    return response.json()