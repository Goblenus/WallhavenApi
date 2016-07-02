import logging
import requests
from bs4 import BeautifulSoup


class WallhavenApi:

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

    @staticmethod
    def _get_images_page_data(categories, purity, resolutions, ratios, sorting, order, page):
        page_data = requests.get('https://alpha.wallhaven.cc/search', params={"categories": categories,
                                                                              "purity": purity,
                                                                              "resolutions": resolutions,
                                                                              "ratios": ratios,
                                                                              "sorting": sorting,
                                                                              "order": order,
                                                                              "page": page},
                                 verify=False)

        logging.debug("Page request code %d", page_data.status_code)

        if page_data.status_code != 200:
            return None

        return page_data

    @staticmethod
    def _get_image_numbers(categories, purity, resolutions, ratios, sorting, order, page):
        logging.debug("Trying obtain image number")

        page_data = WallhavenApi._get_images_page_data(categories, purity, resolutions, ratios, sorting, order, page)

        if page_data is None:
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
        images_urls = []

        for image_number in images_numbers:
            images_urls.append('https://wallpapers.wallhaven.cc/wallpapers/full/wallhaven-{0}.jpg'
                               .format(str(image_number)))

        return images_urls
