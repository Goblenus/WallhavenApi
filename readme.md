# Wallhaven API for Python
[![Build Status](https://travis-ci.org/Goblenus/WallhavenApi.svg?branch=master)](https://travis-ci.org/Goblenus/WallhavenApi)

Feel free to add an issue.

## Description
Not implemented

## Quick Documentation
Import WallhavenApi package:
```python
import WallhavenApi
```
Initialize WallhavenApi:
```python
wallhaven_api= WallhavenApi.WallhavenApi()
```
If you have an account on **[Wallhaven](https://wallhaven.cc)**, you can use it to login and access all available wallpapers:
```python
wallhaven_api = WallhavenApi.WallhavenApi(username="username", password="password")
```
You can also use secure connection to **[Wallhaven](https://wallhaven.cc)**:
```python
wallhaven_api = WallhavenApi.WallhavenApi(verify_connection=True)
```
## Methods
---
##### `get_pages_count` - get pages count of request
_Parameters:_

* category_general {Boolean} - search in General category
* category_anime {Boolean} - search in Anime category
* category_people {Boolean} - search in People category
* purity_sfw {Boolean} - images with sfw purity
* purity_sketchy {Boolean} - images with sketchy purity
* purity_nsfw {Boolean} - images with nsfw purity
* resolutions {String} - string of resolutions (specify a comma, can be empty)
* ratios {String} - string of ratios (specify a comma, can be empty)
* sorting {String} - one of this: relevance, random, date_added, views, favorites
* order {String} - one of this: desc, asc
* page {Int} - page of images
* search_query {String} - search query

_Return:_ **{Int, None}** - count of pages

---

##### `get_images_numbers` - get list of images numbers
_Parameters:_

* category_general {Boolean} - search in General category
* category_anime {Boolean} - search in Anime category
* category_people {Boolean} - search in People category
* purity_sfw {Boolean} - images with sfw purity
* purity_sketchy {Boolean} - images with sketchy purity
* purity_nsfw {Boolean} - images with nsfw purity
* resolutions {String} - string of resolutions (specify a comma, can be empty)
* ratios {String} - string of ratios (specify a comma, can be empty)
* sorting {String} - one of this: relevance, random, date_added, views, favorites
* order {String} - one of this: desc, asc
* page {Int} - page of images
* search_query {String} - search query

_Return:_ **{[Strings]}** - array of images numbers

---

##### `is_image_exists` - check if image exists
_Parameters:_

* image_number {String} - image number

_Return:_ **{Boolean}** - image exists

---

##### `get_image_data` - get image data
_Parameters:_

* image_number {String} - image number
* uploader {Boolean} - get uploader
* category {Boolean} - get category
* short_url {Boolean} - get short_url
* upload_time {Boolean} - get upload_time
* tags {Boolean} - get tags
* ratio {Boolean} - get ratio
* resolution {Boolean} - get resolution
* image_colors {Boolean} - get image_colors
* favorites {Boolean} - get favorites
* image_url {Boolean} - get image_url
* size {Boolean} - get size
* purity {Boolean} - get purity
* views {Boolean} - get views
* tags_ex {Boolean} - get tags_ex

_Return:_ **{Dict}** - parameters of image

_Example:_
```json
{
	"Uploader": {
		"Username": "Cryzeen",
		"Avatar": {
			"32": "static.wallhaven.cc/images/user/avatar/32/88745_adbc0e09e7ff813ba295ad45516d41f8aac3c300d932d0f8ca009f6d8bc61a6e.jpg",
			"200": "static.wallhaven.cc/images/user/avatar/200/88745_adbc0e09e7ff813ba295ad45516d41f8aac3c300d932d0f8ca009f6d8bc61a6e.jpg"
		}
	},
	"Category": "People",
	"ShortUrl": "https://whvn.cc/341690",
	"UploadTime": "2016-03-01T10:42:09+00:00",
	"Tags": ["women", "Asian", "brown eyes", "lingerie", "cleavage", "black bras", "black panties", "high heels", "red lipstick"],
	"Ratio": "Non-standard",
	"Resolution": "2048x1367",
	"ImageColors": ["#cccccc", "#424153", "#999999", "#996633", "#ffffff"],
	"Favorites": 20,
	"ImageUrl": "https://wallpapers.wallhaven.cc/wallpapers/full/wallhaven-341690.jpg",
	"Size": "480.8 KiB",
	"Purity": "Sketchy",
	"Views": 811,
	"TagsEx": [
		{"Type": "sfw", "Name": "women", "Id": "222"},
		{"Type": "sfw", "Name": "Asian", "Id": "449"},
		{"Type": "sfw", "Name": "brown eyes", "Id": "2717"},
		{"Type": "sketchy", "Name": "lingerie", "Id": "297"},
		{"Type": "sketchy", "Name": "cleavage", "Id": "547"},
		{"Type": "sketchy", "Name": "black bras", "Id": "11871"},
		{"Type": "sketchy", "Name": "black panties", "Id": "8159"},
		{"Type": "sfw", "Name": "high heels", "Id": "296"},
		{"Type": "sfw", "Name": "red lipstick", "Id": "12540"}
	]
}
```

---

##### `login` - log in to wallhaven

_Return:_ **{Boolean}** - status of log in

---

##### `logout` - log out from wallhaven

_Return:_ **{Boolean}** - status of log out

---

##### `download_image` - download image to file
_Parameters:_

* image_number {String} - image number
* file_path {String} - path to file
* chunk_size {Number} - downloading chunk size

_Return:_ **{Boolean}** - status of downloading

---
##### `image_tag_delete` - delete image tag
_Parameters:_

* image_number {String} - image number
* tag_id {String} - tag id (can be obtained from get_image_data)

_Return:_ **{Boolean}** - status of action

---

##### `image_tag_add` - add tag to image
_Parameters:_

* image_number {String} - image number
* tag_name {String} - tag name

_Return:_ **{Boolean}** - status of action

---

##### `image_change_purity` - change image purity
_Parameters:_

* image_number {String} - image number
* purity {String} - purity (can be one of: ["sfw", "sketchy", "nsfw"])

_Return:_ **{Boolean}** - status of action

---

##### `get_image_uploader` - get image uploader
_Parameters:_

* image_number {String} - image number

_Return:_ **{Dict}** - uploader

---

##### `get_image_category` - get image category
_Parameters:_

* image_number {String} - image number

_Return:_ **{String}** - cetegory

---

##### `get_image_short_url` - get short url
_Parameters:_

* image_number {String} - image number

_Return:_ **{String}** - short url

---

##### `get_image_upload_time` - get upload time
_Parameters:_

* image_number {String} - image number

_Return:_ **{String}** - upload time

---

##### `get_image_ratio` - get ratio
_Parameters:_

* image_number {String} - image number

_Return:_ **{String}** - ratio

---

##### `get_image_resolution` - get resolution
_Parameters:_

* image_number {String} - image number

_Return:_ **{String}** - resolution

---

##### `get_image_colors` - get colors
_Parameters:_

* image_number {String} - image number

_Return:_ **{[String]}** - array of colors

---

##### `get_image_favorites` - get favorites
_Parameters:_

* image_number {String} - image number

_Return:_ **{Int}** - favorites

---

##### `get_image_url` - get url
_Parameters:_

* image_number {String} - image number

_Return:_ **{String}** - url

---

##### `get_image_size` - get size
_Parameters:_

* image_number {String} - image number

_Return:_ **{String}** - size

---

##### `get_image_purity` - get purity
_Parameters:_

* image_number {String} - image number

_Return:_ **{String}** - purity

---

##### `get_image_views` - get views
_Parameters:_

* image_number {String} - image number

_Return:_ **{Int}** - views

---

##### `get_image_tags_ex` - get tags
_Parameters:_

* image_number {String} - image number

_Return:_ **{{Tags}}** - dict of tags

---