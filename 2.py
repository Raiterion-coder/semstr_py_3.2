import asyncio
import aiohttp

servic_ip = {
    'ipify': 'https://api.ipify.org?format=json',
    'ip-api': 'http://ip-api.com/json/'
}


async def get_ip(session, name, url):
    try:
        async with session.get(url, timeout=5) as resp:
            if resp.status == 200:
                data = await resp.json()
                ip = data.get('ip') or data.get('query')
                return name, ip
    except:
        return None


async def main():
    async with aiohttp.ClientSession() as session:
        tasks = [get_ip(session, name, url) for name, url in servic_ip.items()]
        done, _ = await asyncio.wait(
            [asyncio.create_task(get_ip(session, name, url)) for name, url in servic_ip.items()],
            return_when=asyncio.FIRST_COMPLETED
        )
        for d in done:
            result = d.result()
            if result:
                name, ip = result
                print(f"Твой ip: {ip}, с сайта: {name}")
                break


if __name__ == '__main__':
    asyncio.run(main())
