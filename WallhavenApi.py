import logging
import requests
from bs4 import BeautifulSoup
import threading
import os


class WallhavenApi:
    def __init__(self, username=None, password=None, verify_connection=False):
        self.verify_connection = verify_connection

        self.wallhaven_session = requests.Session()
        self.request_lock = threading.Lock()

        self.username = username
        self.password = password

        self.token = ""

        self.logged_in = self.login()

    def login(self):
        if self.logged_in:
            return True

        if self.username is None or not len(self.username) or self.password is None or not len(self.password):
            return False

        home_page = self._wallhaven_get("https://alpha.wallhaven.cc/", verify=self.verify_connection)

        if home_page.status_code != 200:
            return False

        token_tag = BeautifulSoup(home_page.text, "html.parser")\
            .select('#login > input[name="_token"]')

        if len(token_tag) == 0:
            return False

        self.token = token_tag[0].attrs['value']

        page = self._wallhaven_post("https://alpha.wallhaven.cc/auth/login", data={"username": self.username,
                                                                                   "password": self.password,
                                                                                   "_token": self.token},
                                    verify=self.verify_connection)
        if page.status_code != 200:
            return False

        return True

    def logout(self):
        if not self.logged_in:
            return True

        return self._wallhaven_get("https://alpha.wallhaven.cc/auth/logout").status_code == 200

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

    def _get_images_page_data(self, categories, purity, resolutions, ratios, sorting, order, page, search_query=None):
        params = {"categories": categories, "purity": purity, "resolutions": resolutions, "ratios": ratios,
                  "sorting": sorting, "order": order, "page": page}

        if search_query is not None:
            params["q"] = search_query

        page_data = self._wallhaven_get('https://alpha.wallhaven.cc/search', params=params,
                                        verify=self.verify_connection)

        logging.debug("Page request code %d", page_data.status_code)

        return page_data

    def _get_image_page_data(self, image_number):
        logging.debug("Getting image page")
        page_data = self._wallhaven_get('https://alpha.wallhaven.cc/wallpaper/{0}'.format(str(image_number)),
                                        verify=self.verify_connection)

        logging.debug("Page request code %d", page_data.status_code)

        return page_data

    @staticmethod
    def _make_images_urls(images_numbers):
        return ['https://wallpapers.wallhaven.cc/wallpapers/full/wallhaven-{0}.jpg' .format(str(image_number))
                for image_number in images_numbers]

    @staticmethod
    def make_image_url(image_number):
        return 'https://wallpapers.wallhaven.cc/wallpapers/full/wallhaven-{0}.jpg' .format(str(image_number))

    def get_pages_count(self, category_general=True, category_anime=True, category_people=True, purity_sfw=True,
                        purity_sketchy=True, purity_nsfw=False, resolutions="", ratios="", sorting="", order="desc",
                        page=1, search_query=None):
        page_data = self._get_images_page_data(
            str(int(category_general)) + str(int(category_anime)) + str(int(category_people)),
            str(int(purity_sfw)) + str(int(purity_sketchy)) + str(int(purity_nsfw)), resolutions, ratios, sorting,
            order, page, search_query)

        if page_data.status_code != 200:
            return None

        h2_tag = BeautifulSoup(page_data.text, "html.parser")\
            .select("#thumbs > section:nth-of-type(1) > h2")

        if not len(h2_tag):
            return None

        return int(h2_tag[0].text[h2_tag[0].text.rfind("/") + 1:])

    def get_images_urls(self, category_general=True, category_anime=True, category_people=True, purity_sfw=True,
                        purity_sketchy=True, purity_nsfw=False, resolutions="", ratios="", sorting="", order="desc",
                        page=1, search_query=None):
        image_numbers = self.get_images_numbers(category_general, category_anime, category_people, purity_sfw,
                                                purity_sketchy, purity_nsfw, resolutions, ratios, sorting, order, page,
                                                search_query)

        if image_numbers is None:
            return None

        return self._make_images_urls(image_numbers)

    def get_images_numbers(self, category_general=True, category_anime=True, category_people=True, purity_sfw=True,
                           purity_sketchy=True, purity_nsfw=False, resolutions="", ratios="", sorting="", order="desc",
                           page=1, search_query=None):
        logging.debug("Trying obtain image number")

        page_data = self._get_images_page_data(
            str(int(category_general)) + str(int(category_anime)) + str(int(category_people)),
            str(int(purity_sfw)) + str(int(purity_sketchy)) + str(int(purity_nsfw)),
            resolutions, ratios, sorting, order, page, search_query)

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

    def is_image_exists(self, image_number):
        page_data = self._wallhaven_get("https://alpha.wallhaven.cc/wallpaper/{0}".format(str(image_number)))

        if page_data.status_code != 200:
            return False

        section_tag = BeautifulSoup(page_data.text, "html.parser").select("#showcase")

        if not len(section_tag):
            return False

        return True

    def download_image(self, image_number, file_path, chunk_size=4096):
        if not self.is_image_exists(image_number):
            return False

        image_data = requests.get(self.make_image_url(image_number), stream=True, verify=False)

        logging.debug("Image page loaded with code %d", image_data.status_code)

        if image_data.status_code != 200:
            return False

        self.make_image_url(image_number)

        image_abs_path = os.path.abspath(file_path)

        if not os.path.exists(os.path.dirname(image_abs_path)):
            os.makedirs(os.path.dirname(image_abs_path))

        with os.path.abspath(image_abs_path) as image_file:
            for chunk in image_data.iter_content(chunk_size):
                image_file.write(chunk)

        return True

    def get_image_data(self, image_number):
        resolution_tag_selector = "#showcase-sidebar > div > div.sidebar-content > h3"
        color_tag_selector = "#showcase-sidebar > div > div.sidebar-content > ul > li"
        tags_tags_selector = "#tags > li > a:nth-of-type(2)" if self.logged_in else "#tags > li > a:nth-of-type(1)"
        sfw_tag_selector = "#wallpaper-purity-form label.purity.sfw"
        sketchy_tag_selector = "#wallpaper-purity-form label.purity.sketchy"
        nsfw_tag_selector = "#wallpaper-purity-form label.purity.nsfw"
        avatar_tag_selector = "a.avatar.avatar-32 > img"
        username_tag_selector = "a.username.usergroup-2"
        upload_time_tag_selector = "dd.showcase-uploader > time"
        category_tag_selector = "div[data-storage-id=showcase-info] > dl > dd:nth-of-type(2)"
        size_tag_selector = "div[data-storage-id=showcase-info] > dl > dd:nth-of-type(3)"
        views_tag_selector = "div[data-storage-id=showcase-info] > dl > dd:nth-of-type(4)"
        favorites_tag_selector = "div[data-storage-id=showcase-info] > dl > dd:nth-of-type(5) > a"

        page_data = self._get_image_page_data(image_number)

        if page_data.status_code != 200:
            return None

        section_tag = BeautifulSoup(page_data.text, "html.parser").select("#showcase")
        if not len(section_tag):
            return None

        image_data = {"ImageUrl": self.make_image_url(image_number),
                      "Tags": [],
                      "ImageColors": [],
                      "Purity": None,
                      "Uploader": {"Avatar": {"32": None, "200": None}, "Username": None},
                      "ShortUrl": "https://whvn.cc/{0}".format(str(image_number)),
                      "Resolution": None,
                      "Ratio": None,
                      "UploadTime": None,
                      "Category": None,
                      "Size": None,
                      "Views": None,
                      "Favorites": None}

        resolution_tag = BeautifulSoup(page_data.text, "html.parser").select(resolution_tag_selector)
        if len(resolution_tag):
            resolution_tag = resolution_tag[0]
            image_data["Resolution"] = str(resolution_tag.text).replace(" ", "")

            image_data["Ratio"] = resolution_tag.attrs["title"]

        color_tag = BeautifulSoup(page_data.text, "html.parser").select(color_tag_selector)
        if len(color_tag):
            for color_tag in color_tag:
                style = color_tag.attrs["style"]
                image_data["ImageColors"].append(style[style.rfind("#"):])

        tags_tags = BeautifulSoup(page_data.text, "html.parser").select(tags_tags_selector)
        if len(tags_tags):
            for tag_tag in tags_tags:
                image_data["Tags"].append(tag_tag.text)

        sfw_tag = BeautifulSoup(page_data.text, "html.parser").select(sfw_tag_selector)
        if len(sfw_tag):
            if self.logged_in:
                sfw_checkbox_tag = BeautifulSoup(page_data.text, "html.parser").select("#sfw")
                if len(sfw_checkbox_tag):
                    sfw_checkbox_tag = sfw_checkbox_tag[0]
                    if sfw_checkbox_tag.has_attr('checked'):
                        image_data["Purity"] = "SFW"
                else:
                    image_data["Purity"] = "SFW"
            else:
               image_data["Purity"] = "SFW"

        if image_data["Purity"] is None:
            sketchy_tag = BeautifulSoup(page_data.text, "html.parser").select(sketchy_tag_selector)
            if len(sketchy_tag):
                if self.logged_in:
                    sketchy_checkbox_tag = BeautifulSoup(page_data.text, "html.parser").select("#sketchy")
                    if len(sketchy_checkbox_tag):
                        sketchy_checkbox_tag = sketchy_checkbox_tag[0]
                        if sketchy_checkbox_tag.has_attr('checked'):
                            image_data["Purity"] = "Sketchy"
                    else:
                        image_data["Purity"] = "Sketchy"
                else:
                   image_data["Purity"] = "Sketchy"

        if image_data["Purity"] is None:
            nsfw_tag = BeautifulSoup(page_data.text, "html.parser").select(nsfw_tag_selector)
            if len(nsfw_tag):
                if self.logged_in:
                    nsfw_checkbox_tag = BeautifulSoup(page_data.text, "html.parser").select("#nsfw")
                    if len(nsfw_checkbox_tag):
                        nsfw_checkbox_tag = nsfw_checkbox_tag[0]
                        if nsfw_checkbox_tag.has_attr('checked'):
                            image_data["Purity"] = "NSFW"
                    else:
                        image_data["Purity"] = "NSFW"
                else:
                   image_data["Purity"] = "NSFW"

        avatar_tag = BeautifulSoup(page_data.text, "html.parser").select(avatar_tag_selector)
        if len(avatar_tag):
            avatar_tag = avatar_tag[0]
            avatar_url = avatar_tag.attrs["src"]
            if avatar_url[:2] == "//":
                avatar_url = avatar_url[2:]
            image_data["Uploader"]["Avatar"] = {"32": avatar_url, "200": avatar_url.replace("/32/", "/200/")}

        username_tag = BeautifulSoup(page_data.text, "html.parser").select(username_tag_selector)
        if len(username_tag):
            username_tag = username_tag[0]
            image_data["Uploader"]["Username"] = username_tag.text

        upload_time_tag = BeautifulSoup(page_data.text, "html.parser").select(upload_time_tag_selector)
        if len(upload_time_tag):
            upload_time_tag = upload_time_tag[0]
            image_data["UploadTime"] = upload_time_tag.attrs["datetime"]

        category_tag = BeautifulSoup(page_data.text, "html.parser").select(category_tag_selector)
        if len(category_tag):
            category_tag = category_tag[0]
            image_data["Category"] = category_tag.text

        size_tag = BeautifulSoup(page_data.text, "html.parser").select(size_tag_selector)
        if len(size_tag):
            size_tag = size_tag[0]
            image_data["Size"] = size_tag.text

        views_tag = BeautifulSoup(page_data.text, "html.parser").select(views_tag_selector)
        if len(views_tag):
            views_tag = views_tag[0]
            image_data["Views"] = int(views_tag.text.replace(",", ""))

        favorites_tag = BeautifulSoup(page_data.text, "html.parser").select(favorites_tag_selector)
        if len(favorites_tag):
            favorites_tag = favorites_tag[0]
            image_data["Favorites"] = int(favorites_tag.text.replace(",", ""))

        return image_data
