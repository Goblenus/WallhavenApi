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

        self.logged_in = False
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

        self.logged_in = not self._wallhaven_get("https://alpha.wallhaven.cc/auth/logout").status_code == 200

        return not self.logged_in

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

        image_data = self._wallhaven_get(self.make_image_url(image_number), stream=True, verify=False)

        logging.debug("Image page loaded with code %d", image_data.status_code)

        if image_data.status_code != 200:
            image_data = self._wallhaven_get(self.make_image_url(image_number, "png"), stream=True, verify=False)
            if image_data.status_code != 200:
                return False

        self.make_image_url(image_number)

        image_abs_path = os.path.abspath(file_path)

        if not os.path.exists(os.path.dirname(image_abs_path)):
            os.makedirs(os.path.dirname(image_abs_path))

        with open(os.path.abspath(image_abs_path), "wb") as image_file:
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
        image_url_selector = "#wallpaper"
        tags_ex_tags_selector = "#tags > .tag"

        page_data = self._get_image_page_data(image_number)

        if page_data.status_code != 200:
            return None

        bs_parsed_page = BeautifulSoup(page_data.text, "html.parser")

        section_tag = bs_parsed_page.select("#showcase")
        if not len(section_tag):
            return None

        image_data = {"ImageUrl": None,
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
                      "Favorites": None,
                      "TagsEx": []}

        resolution_tag = bs_parsed_page.select(resolution_tag_selector)
        if len(resolution_tag):
            resolution_tag = resolution_tag[0]
            image_data["Resolution"] = str(resolution_tag.text).replace(" ", "")

            image_data["Ratio"] = resolution_tag.attrs["title"]

        color_tag = bs_parsed_page.select(color_tag_selector)
        if len(color_tag):
            for color_tag in color_tag:
                style = color_tag.attrs["style"]
                image_data["ImageColors"].append(style[style.rfind("#"):])

        tags_tags = bs_parsed_page.select(tags_tags_selector)
        if len(tags_tags):
            for tag_tag in tags_tags:
                image_data["Tags"].append(tag_tag.text)

        sfw_tag = bs_parsed_page.select(sfw_tag_selector)
        if len(sfw_tag):
            if self.logged_in:
                sfw_checkbox_tag = bs_parsed_page.select("#sfw")
                if len(sfw_checkbox_tag):
                    sfw_checkbox_tag = sfw_checkbox_tag[0]
                    if sfw_checkbox_tag.has_attr('checked'):
                        image_data["Purity"] = "SFW"
                else:
                    image_data["Purity"] = "SFW"
            else:
               image_data["Purity"] = "SFW"

        if image_data["Purity"] is None:
            sketchy_tag = bs_parsed_page.select(sketchy_tag_selector)
            if len(sketchy_tag):
                if self.logged_in:
                    sketchy_checkbox_tag = bs_parsed_page.select("#sketchy")
                    if len(sketchy_checkbox_tag):
                        sketchy_checkbox_tag = sketchy_checkbox_tag[0]
                        if sketchy_checkbox_tag.has_attr('checked'):
                            image_data["Purity"] = "Sketchy"
                    else:
                        image_data["Purity"] = "Sketchy"
                else:
                   image_data["Purity"] = "Sketchy"

        if image_data["Purity"] is None:
            nsfw_tag = bs_parsed_page.select(nsfw_tag_selector)
            if len(nsfw_tag):
                if self.logged_in:
                    nsfw_checkbox_tag = bs_parsed_page.select("#nsfw")
                    if len(nsfw_checkbox_tag):
                        nsfw_checkbox_tag = nsfw_checkbox_tag[0]
                        if nsfw_checkbox_tag.has_attr('checked'):
                            image_data["Purity"] = "NSFW"
                    else:
                        image_data["Purity"] = "NSFW"
                else:
                   image_data["Purity"] = "NSFW"

        avatar_tag = bs_parsed_page.select(avatar_tag_selector)
        if len(avatar_tag):
            avatar_tag = avatar_tag[0]
            avatar_url = avatar_tag.attrs["src"]
            if avatar_url[:2] == "//":
                avatar_url = avatar_url[2:]
            image_data["Uploader"]["Avatar"] = {"32": avatar_url, "200": avatar_url.replace("/32/", "/200/")}

        username_tag = bs_parsed_page.select(username_tag_selector)
        if len(username_tag):
            username_tag = username_tag[0]
            image_data["Uploader"]["Username"] = username_tag.text

        upload_time_tag = bs_parsed_page.select(upload_time_tag_selector)
        if len(upload_time_tag):
            upload_time_tag = upload_time_tag[0]
            image_data["UploadTime"] = upload_time_tag.attrs["datetime"]

        category_tag = bs_parsed_page.select(category_tag_selector)
        if len(category_tag):
            category_tag = category_tag[0]
            image_data["Category"] = category_tag.text

        size_tag = bs_parsed_page.select(size_tag_selector)
        if len(size_tag):
            size_tag = size_tag[0]
            image_data["Size"] = size_tag.text

        views_tag = bs_parsed_page.select(views_tag_selector)
        if len(views_tag):
            views_tag = views_tag[0]
            image_data["Views"] = int(views_tag.text.replace(",", ""))

        favorites_tag = bs_parsed_page.select(favorites_tag_selector)
        if len(favorites_tag):
            favorites_tag = favorites_tag[0]
            image_data["Favorites"] = int(favorites_tag.text.replace(",", ""))

        image_url_tag = bs_parsed_page.select(image_url_selector)
        if len(image_url_tag):
            image_url_tag = image_url_tag[0]
            image_data["ImageUrl"] = image_url_tag.attrs["src"].replace("//", "https://")

        tags_ex_tags = bs_parsed_page.select(tags_ex_tags_selector)
        if len(tags_ex_tags):
            for tag_ex_tag in tags_ex_tags:
                tag_ex = {"Name": tag_ex_tag.select(".tagname")[0].text, "Id": tag_ex_tag.attrs["data-tag-id"],
                          "Type": None}

                for class_name in tag_ex_tag.attrs["class"]:
                    if "tag-" in class_name:
                        tag_ex["Type"] = class_name[4:]
                        break

                image_data["TagsEx"].append(tag_ex)

        return image_data

    def image_tag_delete(self, image_number, tag_id):
        if not self.logged_in:
            return False
        response = self._wallhaven_post("https://alpha.wallhaven.cc/wallpaper/tag/remove/{0}/{1}?_token={2}"
            .format(str(tag_id), str(image_number), str(self.token)))
        return response.status_code == 200 and response.json()["status"]

    def image_tag_add(self, image_number, tag_name):
        if not self.logged_in:
            return False
        response = self._wallhaven_post("https://alpha.wallhaven.cc/wallpaper/tag/add",
                                        data={"tag_name": str(tag_name), "wallpaper_id": str(image_number),
                                              "wallpaper_group": str(image_number), "_token": self.token})
        return response.status_code == 200 and response.json()["status"]

    def image_change_purity(self, image_number, purity):
        if not self.logged_in or str(purity) not in ["sfw", "sketchy", "nsfw"]:
            return False
        response = self._wallhaven_post("https://alpha.wallhaven.cc/wallpaper/purity",
                                        data={"wallpaper_id": str(image_number), "purity": str(purity)})
        return response.status_code == 200 and response.json()["status"]