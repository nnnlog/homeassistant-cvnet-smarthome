import json

import aiohttp



class InquirySiteApi:
    @staticmethod
    async def get_region_list(websession: aiohttp.ClientSession) -> list[str]:
        response = await (await websession.get("https://smartlife.uasis.com/api/getregioninfo.do?clientname=CV")).json()

        regions = list(map(lambda x: x["local_name"], response["list"]))

        return regions

    @staticmethod
    async def get_site_list(websession: aiohttp.ClientSession, region: str) -> list[dict[str, str]]:
        response = await (await websession.get(
            f"https://smartlife.uasis.com/api/getsiteinfo.do?clientname=CV&local_name={region}")).json()

        sites = list(
            map(lambda x: {"label": x["apt_name"], "value": json.dumps({"url": x["url"], "name": x["apt_name"]})},
                response["list"]))

        return sites
