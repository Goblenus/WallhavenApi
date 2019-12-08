import webview
import http
import threading
import signal
import sys
from wallhavenapi import WallhavenApiV1
from collections import deque
import time
from multiprocessing import Pool

arrow_event = '''
document.onkeydown = function(e) {
    switch (e.keyCode) {
        case 37:
            document.getElementById("image").src="/api/previous_image.png";
            break;
        case 39:
            document.getElementById("image").src="/api/next_image.png";
            break;
    }
};
'''

api = None
wallhaven_api_v1 = WallhavenApiV1()


class Status(object):
    free = "free"
    downloading = "downloading"
    done = "done"


class Api(object):
    def __init__(self):
        global wallhaven_api_v1
        self.wallhaven_api_v1 = wallhaven_api_v1
        self._walpapers_cache = []
        self._walpapers_cache_lock = threading.Lock()
        self._first_downloaded = -1
        self._current_index = 0
        self._cache_count = 7
        self._cache_delete_timeout = 15

        threading.Thread(target=self._work_thread).start()

    def _work_thread(self):
        while True:
            try:
                if self._current_index + self._cache_count > len(self._walpapers_cache):
                    if self._first_downloaded == -1:
                        page = 1
                    else:
                        page = self._walpapers_cache[-1]["page"] + 1

                    while True:
                        try:
                            data = self.wallhaven_api_v1.search(page=page)
                            print(f"Page data: {page}")
                            break
                        except:
                            time.sleep(5)

                    wallpapers = []

                    for wallpaper in data["data"]:
                        wallpapers.append({"page": page, "status": Status.free, "lock": threading.Lock(), "data": None, 
                            "id": wallpaper["id"], "end": False, "deleteTime": None})

                    if len(data["data"]) != 24:
                        wallpapers[-1]["end"] = True

                    self._walpapers_cache.extend(wallpapers)

                    if self._first_downloaded == -1:
                        self._first_downloaded = len(wallpapers)

                for i in range(len(self._walpapers_cache)):
                    with self._walpapers_cache[i]["lock"]:
                        if i < self._current_index - self._cache_count or \
                            i > self._current_index + self._cache_count:
                            if self._walpapers_cache[i]["status"] != Status.done:
                                continue

                            if self._walpapers_cache[i]["deleteTime"] == None:
                                self._walpapers_cache[i]["deleteTime"] = time.time() + self._cache_delete_timeout
                                continue
                            elif time.time() >= self._walpapers_cache[i]["deleteTime"]:
                                print(f"Deleted: {i} - {self._walpapers_cache[i]['id']}")
                                self._walpapers_cache[i]["status"] = Status.free
                                self._walpapers_cache[i]["data"] = None
                        
                        if i >= self._current_index - self._cache_count and \
                            i <= self._current_index + self._cache_count:

                            self._walpapers_cache[i]["deleteTime"] = None

                            if self._walpapers_cache[i]["status"] != Status.free:
                                continue
                        
                            threading.Thread(target=self._download_wallpaper, args=(i,)).start()

            except:
                pass
            finally:
                time.sleep(0.01)

    def _wait_first_downloaded(self):
        while True:
            if self._first_downloaded == -1:
                time.sleep(0.1)
                continue
            
            break

    def _wait_wallpaper_downloaded(self, cache_index):
        while True:
            with self._walpapers_cache[cache_index]["lock"]:
                if self._walpapers_cache[cache_index]["status"] == Status.done:
                    return self._walpapers_cache[cache_index]["data"]
                
            time.sleep(0.1)

    def current_wallpaper(self):
        print(f"Current; Index: {self._current_index}")

        self._wait_first_downloaded()

        if self._first_downloaded == 0:
            return None

        return self._wait_wallpaper_downloaded(self._current_index)

    def next_wallpaper(self):
        print(f"Next; Index: {self._current_index}")

        self._wait_first_downloaded()

        if self._first_downloaded == 0:
            return None

        if self._walpapers_cache[self._current_index]["end"]:
            return self._wait_wallpaper_downloaded(self._current_index)

        self._current_index += 1

        return self._wait_wallpaper_downloaded(self._current_index)

    def previous_wallpaper(self):
        print(f"Last; Index: {self._current_index}")

        self._wait_first_downloaded()

        if self._first_downloaded == 0:
            return None

        if self._current_index == 0:
            return self._wait_wallpaper_downloaded(self._current_index)

        self._current_index -= 1

        return self._wait_wallpaper_downloaded(self._current_index)

    def _download_wallpaper(self, cache_index):
        global wallhaven_api_v1

        with self._walpapers_cache[cache_index]["lock"]:
            if self._walpapers_cache[cache_index]["status"] != Status.free:
                return

            self._walpapers_cache[cache_index]["status"] = Status.downloading
            
            while True:
                try:
                    image = wallhaven_api_v1.download_wallpaper(self._walpapers_cache[cache_index]["id"], None)
                    
                    self._walpapers_cache[cache_index]["data"] = image
                    self._walpapers_cache[cache_index]["status"] = Status.done

                    print(f"Downloaded: {self._walpapers_cache[cache_index]['id']}")
                    
                    return
                except:
                    time.sleep(5)


class RequestHandler(http.server.BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        global api
        self.api = api

        super().__init__(*args, **kwargs)

    def do_GET(self):
        """Respond to a GET request."""
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.send_header("Cache-Control", "no-store, must-revalidate")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        self.end_headers()

        if (self.path == "/"):
            self.wfile.write(b"<html><head><title>Title goes here.</title></head><body>")
            self.wfile.write(b"<img id=\"image\" src=\"/api/current_image.png\" style=\"display: block;width:100%;height:auto;\">")
            self.wfile.write(f"<script>{arrow_event}</script>".encode("utf-8"))
            self.wfile.write(b"</body></html>")
        elif (self.path == "/api/next_image.png"):
            self.wfile.write(self.api.next_wallpaper())
        elif (self.path == "/api/previous_image.png"):
            self.wfile.write(self.api.previous_wallpaper())
        elif (self.path == "/api/current_image.png"):
            self.wfile.write(self.api.current_wallpaper())

def main():
    global api
    api = Api()

    server = http.server.ThreadingHTTPServer(("127.0.0.1", 8001), RequestHandler)

    def server_thread(server):
        server.serve_forever()

    server_thread_handler = threading.Thread(target=server_thread, args=(server, ))
    server_thread_handler.daemon = True
    server_thread_handler.start()

    webview.create_window('Hello world', 'http://127.0.0.1:8001', frameless=True)
    webview.start()

if __name__ == "__main__":
    main()