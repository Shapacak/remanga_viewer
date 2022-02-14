import random
import time
from PIL import Image, ImageTk
import requests
import json
from pprint import pprint
import os
from pathlib import Path
import io

api_url = 'https://api.remanga.org/api'
api_url_get_manga_filters = 'https://api.remanga.org/api/forms/titles/' \
                            '?get=genres&get=categories&get=types&get=status&get=age_limit'
api_url_all_manga = 'https://api.remanga.org/api/search/catalog/?ordering=-rating&count=30'
api_url_get_manga = 'https://api.remanga.org/api/titles/'
api_url_get_manga_branch = 'https://api.remanga.org/api/titles/chapters/?branch_id='
api_url_get_manga_chapters = 'https://api.remanga.org/api/titles/chapters/'


def create_json(url, name, dir='/'):
    p = Path(dir, name).with_suffix('.json')
    if not p.parent.is_dir():
        p.parent.mkdir(parents=True)
    if not p.exists():
        r = requests.get(url).json()
        with open(p, 'w', encoding='utf-8') as json_file:
            json.dump(r, json_file)
            return r
    with open(p, 'r', encoding='utf-8') as json_file:
        json_r = json.load(json_file)
        return json_r


def image_creator(url, name, dir):
    p = Path(dir, name).with_suffix('.jpg')
    if not p.is_file():
        image_response = requests.get(url)
        with open(p, 'bw') as imgf:
            imgf.write(image_response.content)
    return str(p)


def download_frame_with_dict(url, path):
  if not path.is_file():
    time.sleep(random.randrange(2, 4))
    frame_response = requests.get(url)
    with open(path, 'bw') as imgf:
      imgf.write(frame_response.content)
  return path

def download_frame_with_list(path, frame_parts):
    frame_page = str(frame_parts[0]['page'])
    frame_path = Path(path, frame_page).with_suffix('.jpg')
    if not frame_path.is_file():
        parts = []
        for part in frame_parts:
            response_img = requests.get(part['link'])
            img = Image.open(io.BytesIO(response_img.content))
            parts.append(img)
            time.sleep(random.randrange(1, 3))
        widths, heights = zip(*(i.size for i in parts))

        total_width = max(widths)
        max_height = sum(heights)

        new_im = Image.new('RGB', (total_width, max_height))

        y_offset = 0
        for im in parts:
            new_im.paste(im, (0, y_offset))
            y_offset += im.size[1]

        new_im.save(frame_path)
    return frame_path


def view_manga_catalog():
    all_manga_json = create_json(api_url_all_manga, 'all manga')
    # pprint(all_manga_json['content'])
    catalog_dict = {x['rus_name']: [x['dir'], x['en_name']] for x in all_manga_json['content']}
    return catalog_dict


def view_manga_page(manga_dir, manga_name):
    manga_page = create_json(api_url_get_manga + manga_dir, manga_name, manga_dir)
    br = max(manga_page['content']['branches'], key=lambda x: x['count_chapters'])
    branch_manga = create_json(api_url_get_manga_branch + str(br['id']), 'branch', manga_dir)
    branch_list = []
    for i in reversed(branch_manga['content']):
        if not i['is_paid']:
            branch_list.append({'chapter': i['chapter'],
                                'tome': i['tome'],
                                'name': i['name'],
                                'id': i['id']})

    description = manga_page['content']['description']
    img_url = 'https://remanga.org' + manga_page['content']['img']['mid']
    img = image_creator(img_url, manga_name, manga_dir)
    page_dict = {'branch': branch_list, 'description': description, 'img': img, 'manga_dir': manga_dir}
    return page_dict


def view_manga(tome, chapter, name, id, manga_dir):
    if not name:
        name = chapter
    path_dir = Path(manga_dir, tome, chapter)
    chapter_response = create_json(api_url_get_manga_chapters + id, name, path_dir)
    frames = chapter_response['content']['pages']
    frames_list = []
    if type(frames[0]) is list:
        for i in frames:
            fr = download_frame_with_list(path_dir, i)
            frames_list.append(fr)
    else:
        for frame in frames:
            frame_link = frame['link']
            frame_page = str(frame['page'])
            frame_path = Path(path_dir, frame_page).with_suffix('.jpg')
            fr = download_frame_with_dict(frame_link, frame_path)
            frames_list.append(fr)

    return frames_list

