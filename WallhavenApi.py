import logging
import requests
from bs4 import BeautifulSoup
import threading


class WallhavenApi:
    def __init__(self, username=None, password=None, verify_connection=False):
        self.verify_connection = verify_connection

        self.wallhaven_session = requests.Session()
        self.request_lock = threading.Lock()

        self.username = username
        self.password = password

        self.logged_in = False

        if self.username is not None and len(self.username) and password is not None and len(self.password):
            self._login()

    def _login(self):
        home_page = self._wallhaven_get("https://alpha.wallhaven.cc/", verify=self.verify_connection)

        if home_page.status_code != 200:
            return

        token_tag = BeautifulSoup(home_page.text, "html.parser")\
            .select('#login > input[name="_token"]')

        if len(token_tag) == 0:
            return

        page = self._wallhaven_post("https://alpha.wallhaven.cc/auth/login", data={"username": self.username,
                                                                                   "password": self.password,
                                                                                   "_token":
                                                                                       token_tag[0].attrs['value']},
                                    verify=self.verify_connection)
        if page.status_code != 200:
            return

        self.logged_in = True

    def _wallhaven_post(self, url, data=None, json=None, **kwargs):
        self.request_lock.acquire()
        result = self.wallhaven_session.post(url, data, json, **kwargs)
        self.request_lock.release()
        return result

    def _wallhaven_get(self, url, **kwargs):
        self.request_lock.acquire()
        result = self.wallhaven_session.get(url, **kwargs)
        self.request_lock.release()
        return result

    def get_images_urls(self, category_general=True, category_anime=True, category_people=True, purity_sfw=True,
                        purity_sketchy=True, purity_nsfw=False, resolutions="", ratios="", sorting="", order="desc",
                        page=1):
        image_numbers = \
            self._get_image_numbers(
                str(int(category_general)) + str(int(category_anime)) + str(int(category_people)),
                str(int(purity_sfw)) + str(int(purity_sketchy)) + str(int(purity_nsfw)),
                resolutions, ratios, sorting, order, page)

        if image_numbers is None:
            return None

        return self._make_images_urls(image_numbers)

    def _get_image_numbers(self, categories, purity, resolutions, ratios, sorting, order, page):
        logging.debug("Trying obtain image number")

        page_data = self._wallhaven_get('https://alpha.wallhaven.cc/search', params={"categories": categories,
                                                                                     "purity": purity,
                                                                                     "resolutions": resolutions,
                                                                                     "ratios": ratios,
                                                                                     "sorting": sorting,
                                                                                     "order": order,
                                                                                     "page": page},
                                        verify=self.verify_connection)

        logging.debug("Page request code %d", page_data.status_code)

        if page_data.status_code != 200:
            return None

        figures_tags = BeautifulSoup(page_data.text, "html.parser")\
            .select("#thumbs > section:nth-of-type(1) > ul > li > figure[data-wallpaper-id]")

        logging.debug("Found %d images tags", len(figures_tags))

        if not len(figures_tags):
            return None

        images_numbers = []

        for figure_tag in figures_tags:
            images_numbers.append(figure_tag.attrs['data-wallpaper-id'])

        return images_numbers

    @staticmethod
    def _make_images_urls(images_numbers):
        return ['https://wallpapers.wallhaven.cc/wallpapers/full/wallhaven-{0}.jpg' .format(str(image_number))
                for image_number in images_numbers]
