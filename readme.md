# Wallhaven API for Python

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

_Return:_ **{Json}** - parameters of image

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
* image_path {String} - path to file
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

Feel free to add an issue.