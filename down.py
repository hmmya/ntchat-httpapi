#正雨 @ 1695960757
import os.path
import time
import requests
from xdg import get_download_dir
from models import SendMediaReqModel


def get_local_path(datax):
    if "file_path" in datax.keys():
        if os.path.isfile(datax["file_path"]):
            return datax["file_path"]
    if "url" not in datax.keys():
        return None
    data = requests.get(datax["url"]).content
    temp_file = os.path.join(get_download_dir(), str(time.time_ns()))
    with open(temp_file, 'wb') as fp:
        fp.write(data)
    return temp_file


