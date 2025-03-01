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


def update_readme_voice_count(voice_count):
    readme_path = PROGRAM_PATH / "README.md"

    with open(readme_path, "r") as f:
        lines = f.readlines()

    for i, line in enumerate(lines):
        if line.startswith("## Voice Count"):
            lines[i : i + 3] = f"## Voice Count\n\n- {voice_count} voices\n"

    with open(readme_path, "w") as f:
        f.writelines(lines)


def download_voice(id, src, category, retry=0):
    voice_path = VOICES_PATH / category / f"{id}.mp3"

    if voice_path.exists():
        return True

    url = src.replace("./", "https://leiros.cloudfree.jp/usbtn/")

    res = requests.get(url)

    voice_binary = res.content

    # If the file is not an mp3 file, retry
    if res.headers["Content-Type"] != "audio/mpeg":
        if retry < 5:
            return download_voice(id, src, category, retry + 1)
        else:
            print(f"Failed to download {id} from {src}")
            return False

    with open(voice_path, "wb") as f:
        f.write(voice_binary)

    return False


btn_url = "https://leiros.cloudfree.jp/usbtn/usbtn.html"

html_string = requests.get(btn_url).text.encode("latin1").decode("utf8")

id_dict = find_id_relate_src(html_string)
category_dict = find_category_and_id(html_string)

new_updated = []

print(len(id_dict), "voices found")
update_readme_voice_count(len(id_dict))

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
