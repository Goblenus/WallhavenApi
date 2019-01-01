import logging
import requests
import os

def purity(sfw=True, sketchy=True, nsfw=False):
    return "{}{}{}".format(int(sfw), int(sketchy), int(nsfw))


def category(general=True, anime=True, people=False):
    return "{}{}{}".format(int(general), int(anime), int(people))


class Sorting:
    dated_added = "dated_added"
    relevance = "relevance"
    random = "random"
    views = "views"
    favorites = "favorites"
    toplist = "toplist"


class Order:
    # desc used by default
    desc = "desc"
    asc = "asc"


class TopRange:
    one_day = "1d"
    three_days = "3d"
    one_week = "1w"
    one_month = "1M"
    three_months = "3M"
    six_months = "6M"
    one_year = "1y"


def resulution(width, height):
    return "{}x{}".format(width, height)


def ratio(width, height):
    return "{}x{}".format(width, height)


def color(red=0, green=0, blue=0):
    def clamp(x):
        max(0, min(x, 255))
    
    return "{0:02x}{1:02x}{2:02x}".format(clamp(red), clamp(green), clamp(blue))


def combine_params(*args):
    return ",".join(str(x) for x in args)


class RequestsLimitError(Exception):
    def __init__(self):
        super().__init__("You have exceeded requests limit. Please try later.")


class ApiKeyError(Exception):
    def __init__(self):
        super().__init__("Bad api key. Check it please.")


class UnhandledException(Exception):
    def __init__(self):
        super().__init__("Somthing went wrong. Please submit this issue to "
                         "https://github.com/Goblenus/WallhavenApi/issues.")


class NoWallpaperError(Exception):
    def __init__(self, wallpaper_id):
        super().__init__("No wallpaper with id {}".format(wallpaper_id))


class WallhavenApiV1:
    def __init__(self, api_key=None, verify_connection=False, base_url=None, 
                 timeout=(2,5)):
        self.verify_connection = verify_connection
        self.api_key = api_key

        self.base_url = base_url if base_url is not None else "https://wallhaven.cc/api/v1"

        self.timeout = timeout

    def search(self, q=None, category=None, purity=None, sorting=None, order=None, topRange=None, atleast=None, 
               resolutions=None, ratios=None, colors=None, page=None):
        params = {}
        if self.api_key is not None:
            params["apikey"] = self.api_key

        if q is not None:
            params["q"] = q

        if category is not None:
            params["category"] = category

        if purity is not None:
            params["purity"] = purity

        if sorting is not None:
            params["sorting"] = sorting

        if order is not None:
            params["order"] = order

        if topRange is not None:
            params["topRange"] = topRange

        if atleast is not None:
            params["atleast"] = atleast

        if resolutions is not None:
            params["resolutions"] = resolutions

        if ratios is not None:
            params["ratios"] = ratios

        if colors is not None:
            params["colors"] = colors

        if page is not None:
            params["page"] = page

        response = requests.get("{}{}".format(self.base_url, "/search"), params=params, timeout=self.timeout, 
                                verify=self.verify_connection)

        if response.status_code == 429:
            raise RequestsLimitError

        if response.status_code == 401:
            raise ApiKeyError

        if response.status_code != 200:
            raise UnhandledException

        try:
            search_data = response.json()
        except:
            raise UnhandledException

        return search_data

    def wallpaper(self, wallpaper_id):
        params = {}
        if self.api_key is not None:
            params["apikey"] = self.api_key

        response = requests.get("{}{}/{}".format(self.base_url, "/w", wallpaper_id), params=params, 
                                timeout=self.timeout, verify=self.verify_connection)

        if response.status_code == 429:
            raise RequestsLimitError

        if response.status_code == 401:
            raise ApiKeyError

        if response.status_code != 200:
            raise UnhandledException

        try:
            wallpaper_data = response.json()
        except:
            raise UnhandledException

        return wallpaper_data

    def is_walpaper_exists(self, wallpaper_id):
        return "error" not in self.wallpaper(wallpaper_id)

    def download_walpaper(self, wallpaper_id, file_path, chunk_size=4096):
        wallpaper_data = self.wallpaper(wallpaper_id)

        if "error" in wallpaper_data:
            raise NoWallpaperError(wallpaper_id)

        wallpaper = requests.get(wallpaper_data["data"]["path"], stream=True, timeout=self.timeout, 
                                 verify=self.verify_connection)

        if wallpaper.status_code != 200:
            raise UnhandledException

        save_path = os.path.abspath(file_path)
        save_directory_path = os.path.dirname(save_path)

        if not os.path.exists(save_directory_path):
            os.makedirs(save_directory_path)

        with open(save_path, "wb") as image_file:
            for chunk in wallpaper.iter_content(chunk_size):
                image_file.write(chunk)

if __name__ == "__main__":
    wh = WallhavenApiV1(base_url="http://stest39.wallhaven.cc/api/v1")

    print(wh.search())