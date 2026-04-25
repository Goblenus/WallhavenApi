import unittest
from unittest.mock import Mock, patch
from wallhavenapi import (
    WallhavenApiV1, Category, Purity, Sorting, Order, TopRange, Color, Type,
    RequestsLimitError, ApiKeyError, UnhandledException, NoWallpaperError, Seed
)
import os
import datetime
import time
import tempfile
import json


class TestWallhavenApiV1(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.wallhaven_api = WallhavenApiV1(api_key=os.getenv('APIKEY', None), verify_connection=False, 
                                            base_url="http://wallhaven.cc/api/v1", 
                                            requestslimit_timeout=(15, 5))
    
    def test_search(self):
        search_data = self.wallhaven_api.search()

        self.assertIn("data", search_data)
        self.assertIn("meta", search_data)

    def test_search_categories(self):
        for category in list(Category):
            search_data = self.wallhaven_api.search(categories=category)

            for wallpaper_data in search_data["data"]:
                self.assertEqual(category.value, wallpaper_data["category"])

    def test_search_purities(self):
        for purity in list(Purity):
            search_data = self.wallhaven_api.search(purities=purity)

            for wallpaper_data in search_data["data"]:
                self.assertEqual(purity.value, wallpaper_data["purity"])

    def test_search_sorting(self):
        for sorting_method in list(Sorting):
            search_data = self.wallhaven_api.search(sorting=sorting_method)
            self.assertIn("data", search_data)

    def search_sorting_dated_added(self, order):
        def parse_datetime(datetime_string):
            # Format: 2018-10-31 01:23:10.000000
            return datetime.datetime.strptime(datetime_string, "%Y-%m-%d %H:%M:%S")
        
        search_data = self.wallhaven_api.search(sorting=Sorting.date_added, order=order)
        for i in range(len(search_data["data"]) - 1):
            datetime_1 = parse_datetime(search_data["data"][i]["created_at"])
            datetime_2 = parse_datetime(search_data["data"][i + 1]["created_at"])
            self.assertGreaterEqual(datetime_1, datetime_2) \
            if order == Order.desc else self.assertLessEqual(datetime_1, datetime_2)

    def test_search_sorting_dated_added_asc(self):
        self.search_sorting_dated_added(Order.asc)

    def test_search_sorting_dated_added_desc(self):
        self.search_sorting_dated_added(Order.desc)

    def search_sorting_views(self, order):
        search_data = self.wallhaven_api.search(sorting=Sorting.views, order=order)
        for i in range(len(search_data["data"]) - 1):
            views_1 = int(search_data["data"][i]["views"])
            views_2 = int(search_data["data"][i + 1]["views"])
            self.assertGreaterEqual(views_1, views_2) \
            if order == Order.desc else self.assertLessEqual(views_1, views_2)

    @unittest.skip("May content unsorted results. Need help")
    def test_search_sorting_views_asc(self):
        self.search_sorting_views(Order.asc)

    @unittest.skip("May content unsorted results. Need help")
    def test_search_sorting_views_desc(self):
        self.search_sorting_views(Order.desc)

    def search_sorting_favorites(self, order):
        search_data = self.wallhaven_api.search(sorting=Sorting.favorites, order=order)
        for i in range(len(search_data["data"]) - 1):
            favorites_1 = int(search_data["data"][i]["favorites"])
            favorites_2 = int(search_data["data"][i + 1]["favorites"])
            self.assertGreaterEqual(favorites_1, favorites_2) \
            if order == Order.desc else self.assertLessEqual(favorites_1, favorites_2)

    @unittest.skip("May content unsorted results. Need help")
    def test_search_sorting_favorites_asc(self):
        self.search_sorting_favorites(Order.asc)

    @unittest.skip("May content unsorted results. Need help")
    def test_search_sorting_favorites_desc(self):
        self.search_sorting_favorites(Order.desc)

    @unittest.skip("Wallhaven API toplist may return results outside expected date range")
    def test_search_top_range(self):
        for top_range in list(TopRange):
            search_data = self.wallhaven_api.search(top_range=top_range, sorting=Sorting.toplist)
            self.assertIn("data", search_data)

            if str(top_range.value[-1]).endswith("d"):
                timedelta = datetime.timedelta(days=int(top_range.value[:-1]))
            elif str(top_range.value[-1]).endswith("w"):
                timedelta = datetime.timedelta(days=(int(top_range.value[:-1]) * 7))
            elif str(top_range.value[-1]).endswith("M"):
                timedelta = datetime.timedelta(days=(int(top_range.value[:-1]) * 30))
            else:
                timedelta = datetime.timedelta(days=(int(top_range.value[:-1]) * 365))

            for wallpaper in search_data["data"]:
                created_at = datetime.datetime.strptime(wallpaper["created_at"], "%Y-%m-%d %H:%M:%S")

                self.assertGreaterEqual(created_at, datetime.datetime.now() - timedelta)
    
    def test_search_atleast(self):
        search_data = self.wallhaven_api.search(atleast=(1920, 1080))
        for wallpaper in search_data["data"]:
            self.assertGreaterEqual(int(wallpaper["dimension_x"]), 1920)
            self.assertGreaterEqual(int(wallpaper["dimension_y"]), 1080)

    def test_search_resolutions(self):
        search_data = self.wallhaven_api.search(resolutions=(1920, 1080))
        for wallpaper in search_data["data"]:
            self.assertEqual(int(wallpaper["dimension_x"]), 1920)
            self.assertEqual(int(wallpaper["dimension_y"]), 1080)

    def test_search_ratios(self):
        search_data = self.wallhaven_api.search(ratios=(16, 10))
        for wallpaper in search_data["data"]:
            self.assertEqual(float(wallpaper["ratio"]), 1.6)

    def test_search_colors(self):
        for color in list(Color):
            search_data = self.wallhaven_api.search(colors=color)
            for wallpaper in search_data["data"]:
                self.assertIn("colors", wallpaper)
                self.assertIn("#{}".format(color.value), wallpaper["colors"])

    def test_search_page(self):
        search_data = self.wallhaven_api.search()

        self.assertIn("last_page", search_data["meta"])

        if int(search_data["meta"]["last_page"]) > 1:
            search_data = self.wallhaven_api.search(page=2)

            self.assertIn("data", search_data)
            self.assertIn("meta", search_data)
            self.assertIn("current_page", search_data["meta"])
            self.assertEqual(2, int(search_data["meta"]["current_page"]))

    def test_wallpaper(self):
        search_data = self.wallhaven_api.search()

        if not len(search_data["data"]):
            return

        for wallpaper_temp in search_data["data"]:
            self.assertIn("id", wallpaper_temp)

        wallpaper = self.wallhaven_api.wallpaper(search_data["data"][0]["id"])
        self.assertIn("data", wallpaper)

    def test_tag(self):
        search_data = self.wallhaven_api.search()

        for wallpaper_temp in search_data["data"]:
            self.assertIn("id", wallpaper_temp)
            wallpaper = self.wallhaven_api.wallpaper(wallpaper_temp["id"])
            self.assertIn("data", wallpaper)
            self.assertIn("tags", wallpaper["data"])

            if not len(wallpaper["data"]["tags"]):
                continue

            for tag_temp in wallpaper["data"]["tags"]:
                self.assertIn("id", tag_temp)
        
            tag = self.wallhaven_api.tag(wallpaper["data"]["tags"][0]['id'])
            
            self.assertIn("data", tag)
            
            break
    
    def test_search_query_uploader(self):
        search_data = self.wallhaven_api.search()

        self.assertIn("data", search_data)

        if not len(search_data["data"]):
            return None

        wallpaper = self.wallhaven_api.wallpaper(search_data["data"][0]["id"])

        self.assertIn("data", wallpaper)
        self.assertIn("uploader", wallpaper["data"])
        self.assertIn("username", wallpaper["data"]["uploader"])
        
        search_data = self.wallhaven_api.search(q="@{}".format(wallpaper["data"]["uploader"]["username"]))

        self.assertIn("data", search_data)

        self.assertGreater(len(search_data["data"]), 0)

    def test_search_query_id(self):
        search_data = self.wallhaven_api.search()

        for wallpaper_temp in search_data["data"]:
            self.assertIn("id", wallpaper_temp)
            wallpaper = self.wallhaven_api.wallpaper(wallpaper_temp["id"])
            self.assertIn("data", wallpaper)
            self.assertIn("tags", wallpaper["data"])

            if not len(wallpaper["data"]["tags"]):
                continue

            for tag_temp in wallpaper["data"]["tags"]:
                self.assertIn("id", tag_temp)

            search_data = self.wallhaven_api.search(q="id:{}".format(wallpaper["data"]["tags"][0]['id']))
            
            self.assertIn("data", search_data)
            self.assertGreater(len(search_data["data"]), 0)
            break

    def test_search_query_like(self):
        search_data = self.wallhaven_api.search()

        if not len(search_data):
            return

        search_data = self.wallhaven_api.search(q="like:{}".format(search_data["data"][0]['id']))
            
        self.assertIn("data", search_data)
        self.assertIn("meta", search_data)

    def test_search_query_type(self):
        for image_type in Type:
            search_data = self.wallhaven_api.search(q="type:{}".format(image_type.value))
            
            self.assertIn("data", search_data)
            self.assertIn("meta", search_data)

            for wallpaper in search_data["data"]:
                self.assertIn("file_type", wallpaper)
                if image_type in [Type.jpeg, Type.jpg]:
                    self.assertTrue(str(wallpaper["file_type"]).endswith(Type.jpeg.value) \
                                    or str(wallpaper["file_type"]).endswith(Type.jpg.value))
                else:
                    self.assertTrue(str(wallpaper["file_type"]).endswith(image_type.value))
    
    def test_settings(self):
        result = self.wallhaven_api.settings()

        assert result is None if self.wallhaven_api.api_key is None else result is not None

    def test_collections(self):
        result = self.wallhaven_api.collections("ThorRagnarok")

        assert "data" in result
        assert len(result["data"])
        assert "id" in result["data"][0]

    def _get_collections_data(self):
        result = self.wallhaven_api.collections("ThorRagnarok")

        assert "data" in result
        assert len(result["data"])
        assert "id" in result["data"][0]

        return result

    def test_collections(self):
        self._get_collections_data()

    def test_collection_wallpapers(self, page=None):
        collections = self._get_collections_data()

        collections_wallpapers = self.wallhaven_api.collection_wallpapers("ThorRagnarok", 
            collections["data"][0]["id"], page=page)

        assert "data" in collections_wallpapers
        assert "meta" in collections_wallpapers
        assert len(collections_wallpapers["data"])

    def test_collection_wallpapers_page(self):
        self.test_collection_wallpapers(2)

    def test_my_collections_no_api_key(self):
        if self.wallhaven_api.api_key is not None:
            self.skipTest("API key is set")
        result = self.wallhaven_api.my_collections()
        self.assertIsNone(result)

    def test_my_collections_with_api_key(self):
        if self.wallhaven_api.api_key is None:
            self.skipTest("API key is not set")
        result = self.wallhaven_api.my_collections()
        self.assertIsNotNone(result)
        self.assertIn("data", result)


class TestWallhavenApiV1Mocked(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.wallhaven_api = WallhavenApiV1(
            api_key="test_api_key",
            verify_connection=False,
            base_url="http://wallhaven.cc/api/v1",
            requestslimit_timeout=(3, 0)
        )

    def _make_mock_response(self, status_code=200, json_data=None, content=None):
        mock_resp = Mock()
        mock_resp.status_code = status_code
        if json_data is not None:
            mock_resp.json.return_value = json_data
        if content is not None:
            mock_resp.content = content
            mock_resp.iter_content = lambda chunk_size: [content[i:i+chunk_size] for i in range(0, len(content), chunk_size)]
        return mock_resp

    def test_requests_limit_error(self):
        mock_resp = self._make_mock_response(429)
        with patch("requests.request", return_value=mock_resp):
            with self.assertRaises(RequestsLimitError):
                self.wallhaven_api.search()

    def test_requests_limit_error_retry(self):
        call_count = [0]
        def mock_request_func(**kwargs):
            call_count[0] += 1
            return self._make_mock_response(429)
        with patch("requests.request", side_effect=mock_request_func):
            with self.assertRaises(RequestsLimitError):
                self.wallhaven_api.search()
        self.assertEqual(call_count[0], 3)

    def test_api_key_error(self):
        mock_resp = self._make_mock_response(401)
        with patch("requests.request", return_value=mock_resp):
            with self.assertRaises(ApiKeyError):
                self.wallhaven_api.search()

    def test_unhandled_exception_status(self):
        mock_resp = self._make_mock_response(500)
        with patch("requests.request", return_value=mock_resp):
            with self.assertRaises(UnhandledException):
                self.wallhaven_api.search()

    def test_unhandled_exception_json_parse(self):
        mock_resp = self._make_mock_response(200)
        mock_resp.json.side_effect = json.JSONDecodeError("err", "doc", 0)
        with patch("requests.request", return_value=mock_resp):
            with self.assertRaises(UnhandledException):
                self.wallhaven_api.search()

    def test_api_key_injection_no_existing_params(self):
        api = WallhavenApiV1(api_key="secret_key")
        mock_resp = self._make_mock_response(200, {"data": [], "meta": {}})
        with patch("requests.request", return_value=mock_resp) as mock_req:
            api.search()
            call_kwargs = mock_req.call_args[1]
            self.assertEqual(call_kwargs["params"]["apikey"], "secret_key")

    def test_api_key_injection_existing_params(self):
        api = WallhavenApiV1(api_key="secret_key")
        mock_resp = self._make_mock_response(200, {"data": [], "meta": {}})
        with patch("requests.request", return_value=mock_resp) as mock_req:
            api.search(q="test")
            call_kwargs = mock_req.call_args[1]
            self.assertEqual(call_kwargs["params"]["apikey"], "secret_key")
            self.assertEqual(call_kwargs["params"]["q"], "test")

    def test_seed_generate(self):
        seed = Seed.generate()
        self.assertEqual(len(seed), 6)
        self.assertTrue(seed.isalnum())

    def test_requests_limit_error_message(self):
        exc = RequestsLimitError()
        self.assertIn("exceeded requests limit", str(exc))

    def test_api_key_error_message(self):
        exc = ApiKeyError()
        self.assertIn("Bad api key", str(exc))

    def test_unhandled_exception_message(self):
        exc = UnhandledException()
        self.assertIn("Somthing went wrong", str(exc))

    def test_no_wallpaper_error_message(self):
        exc = NoWallpaperError("abc123")
        self.assertIn("abc123", str(exc))

    def test_is_walpaper_exists_true(self):
        mock_data = {"data": {"id": "abc123"}}
        mock_resp = self._make_mock_response(200, mock_data)
        with patch("requests.request", return_value=mock_resp):
            result = self.wallhaven_api.is_walpaper_exists("abc123")
            self.assertTrue(result)

    def test_is_walpaper_exists_false(self):
        mock_data = {"error": "not found"}
        mock_resp = self._make_mock_response(200, mock_data)
        with patch("requests.request", return_value=mock_resp):
            result = self.wallhaven_api.is_walpaper_exists("bad_id")
            self.assertFalse(result)

    def test_download_wallpaper_to_file(self):
        wallpaper_data = {"data": {"path": "http://example.com/wallpaper.png"}}
        mock_wallpaper_resp = self._make_mock_response(200, content=b"PNG_IMAGE_DATA_HERE")
        with patch("requests.request", return_value=self._make_mock_response(200, wallpaper_data)):
            with patch("requests.get", return_value=mock_wallpaper_resp):
                with tempfile.TemporaryDirectory() as tmpdir:
                    filepath = os.path.join(tmpdir, "test_wallpaper.png")
                    result = self.wallhaven_api.download_wallpaper("abc123", filepath)
                    self.assertEqual(result, os.path.abspath(filepath))
                    self.assertTrue(os.path.exists(result))
                    with open(result, "rb") as f:
                        self.assertEqual(f.read(), b"PNG_IMAGE_DATA_HERE")

    def test_download_wallpaper_to_bytes(self):
        wallpaper_data = {"data": {"path": "http://example.com/wallpaper.png"}}
        mock_wallpaper_resp = self._make_mock_response(200, content=b"RAW_IMAGE_BYTES")
        with patch("requests.request", return_value=self._make_mock_response(200, wallpaper_data)):
            with patch("requests.get", return_value=mock_wallpaper_resp):
                result = self.wallhaven_api.download_wallpaper("abc123", None)
                self.assertEqual(result, b"RAW_IMAGE_BYTES")

    def test_download_wallpaper_no_wallpaper_error(self):
        error_data = {"error": "not found"}
        with patch("requests.request", return_value=self._make_mock_response(200, error_data)):
            with self.assertRaises(NoWallpaperError):
                self.wallhaven_api.download_wallpaper("bad_id", "/tmp/test.png")

    def test_download_wallpaper_unhandled_exception(self):
        wallpaper_data = {"data": {"path": "http://example.com/wallpaper.png"}}
        with patch("requests.request", return_value=self._make_mock_response(200, wallpaper_data)):
            with patch("requests.get", return_value=self._make_mock_response(500)):
                with self.assertRaises(UnhandledException):
                    self.wallhaven_api.download_wallpaper("abc123", "/tmp/test.png")

    def test_legacy_download_walpaper(self):
        wallpaper_data = {"data": {"path": "http://example.com/wallpaper.png"}}
        mock_wallpaper_resp = self._make_mock_response(200, content=b"LEGACY_DATA")
        with patch("requests.request", return_value=self._make_mock_response(200, wallpaper_data)):
            with patch("requests.get", return_value=mock_wallpaper_resp):
                with tempfile.TemporaryDirectory() as tmpdir:
                    filepath = os.path.join(tmpdir, "legacy.png")
                    result = self.wallhaven_api.download_walpaper("abc123", filepath)
                    self.assertTrue(os.path.exists(result))

    def test_search_with_seed(self):
        mock_resp = self._make_mock_response(200, {"data": [], "meta": {}})
        with patch("requests.request", return_value=mock_resp) as mock_req:
            self.wallhaven_api.search(seed="abc123")
            call_kwargs = mock_req.call_args[1]
            self.assertEqual(call_kwargs["params"]["seed"], "abc123")

    def test_search_with_top_range(self):
        mock_resp = self._make_mock_response(200, {"data": [], "meta": {}})
        with patch("requests.request", return_value=mock_resp) as mock_req:
            self.wallhaven_api.search(sorting=Sorting.toplist, top_range=TopRange.one_month)
            call_kwargs = mock_req.call_args[1]
            self.assertEqual(call_kwargs["params"]["topRange"], "1M")

    def test_request_to_json_false(self):
        mock_resp = self._make_mock_response(200, {"data": []})
        with patch("requests.request", return_value=mock_resp):
            result = self.wallhaven_api._request(to_json=False, method="get", url="http://test.url")
            self.assertEqual(result.status_code, 200)

    def test_download_wallpaper_creates_directory(self):
        wallpaper_data = {"data": {"path": "http://example.com/wallpaper.png"}}
        mock_wallpaper_resp = self._make_mock_response(200, content=b"DIR_TEST_DATA")
        with patch("requests.request", return_value=self._make_mock_response(200, wallpaper_data)):
            with patch("requests.get", return_value=mock_wallpaper_resp):
                with tempfile.TemporaryDirectory() as tmpdir:
                    subdir = os.path.join(tmpdir, "nonexistent", "subdir")
                    filepath = os.path.join(subdir, "wallpaper.png")
                    result = self.wallhaven_api.download_wallpaper("abc123", filepath)
                    self.assertTrue(os.path.exists(result))


if __name__ == '__main__':
    unittest.main()
