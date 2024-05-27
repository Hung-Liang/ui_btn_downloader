import re
import requests
from pathlib import Path

PROGRAM_PATH = Path(__file__).resolve().parent

VOICES_PATH = PROGRAM_PATH / "voices"
VOICES_PATH.mkdir(exist_ok=True)


def find_id_relate_src(html_string):
    matches = re.findall(r'"id":"(.*?)".*?"src":"(.*?)"', html_string)

    id_dict = {
        match[0]: match[1]
        for match in matches
        if match[0] != "" and match[1] != ""
    }

    return id_dict


def find_category_and_id(html_string):
    class_names = re.findall(r'className:"(.*?)"', html_string)
    id_lists = re.findall(r"idList:\[\s*(.*?)\s*\]", html_string, re.DOTALL)

    category_dict = {}

    for i, class_name in enumerate(class_names):
        category_dict[class_name] = re.findall(r'"id":"(.*?)"', id_lists[i])

    return category_dict


def download_voice(id, src, category):
    voice_path = VOICES_PATH / category / f"{id}.mp3"

    if voice_path.exists():
        return True

    url = src.replace("./", "http://cbtm.html.xdomain.jp//usbtn/")

    voice_binary = requests.get(url).content

    with open(voice_path, "wb") as f:
        f.write(voice_binary)

    return False


btn_url = "http://cbtm.html.xdomain.jp//usbtn/usbtn.html"

html_string = requests.get(btn_url).text.encode("latin1").decode("utf8")

id_dict = find_id_relate_src(html_string)
category_dict = find_category_and_id(html_string)

new_updated = []

for category, ids in category_dict.items():
    category_path = VOICES_PATH / category
    category_path.mkdir(exist_ok=True)

    for id in ids:
        if id not in id_dict:
            continue
        src = id_dict[id]

        if not download_voice(id, src, category):
            new_updated.append([id, src, category])

        del id_dict[id]

OTHERS_PATH = VOICES_PATH / "others"
OTHERS_PATH.mkdir(exist_ok=True)

for id, src in id_dict.items():
    if not download_voice(id, src, "others"):
        new_updated.append([id, src, "others"])

print("new updated:", new_updated)
print("Finished!")
