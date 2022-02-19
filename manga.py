import random
import time
from PIL import Image, ImageTk
import requests
import json
from pprint import pprint
import os
from pathlib import Path
import io
import urllib.parse

api_url = 'https://api.remanga.org/api'
api_url_get_manga_filters = 'https://api.remanga.org/api/forms/titles/' \
                            '?get=genres&get=categories&get=types&get=status&get=age_limit'
api_url_all_manga = 'https://api.remanga.org/api/search/catalog/?ordering=-rating&count=30&page='
api_url_search = 'https://api.remanga.org/api/search/?query='
api_url_get_manga = 'https://api.remanga.org/api/titles/'
api_url_get_manga_branch = 'https://api.remanga.org/api/titles/chapters/?ordering=index&count=60&branch_id='
api_url_get_manga_chapters = 'https://api.remanga.org/api/titles/chapters/'


def create_json(url, name, dir='', load=True):
    p = Path(dir, name).with_suffix('.json')
    if not p.parent.is_dir():
        p.parent.mkdir(parents=True)
    if not p.exists():
        response = requests.get(url).json()
        with open(p, 'w', encoding='utf-8') as json_file:
            json.dump(response, json_file)
            return response
    if load == False:
        with open(p, 'r', encoding='utf-8') as rjson:
            stored_json = json.load(rjson)
            return stored_json
    else:
        response = requests.get(url).json()
        if response['content'] != []:
            with open(p, 'r', encoding='utf-8') as rjson:
                stored_json = json.load(rjson)
            if not next((x for x in stored_json['content'] if x["id"] == response['content'][-1]['id']), None):
                response['content'] = stored_json['content'] + response['content']
                with open(p, 'w', encoding='utf-8') as json_file:
                    json.dump(response, json_file)
                    return response
            else:
                return stored_json
        else:
            return


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

def get_filters():
    all_filters = create_json(api_url_get_manga_filters, 'filters', '', False)
    return all_filters['content']

def filters_string_builder(selected_filters:list):
    filter_string = ''
    for filter in selected_filters:
        if len(filter) == 2:
            filter_string = filter_string + f'&{filter[0]}={filter[1]}'
        else:
            filter_string = filter_string + f'&ordering=-{filter}'
    return filter_string



def view_manga_catalog(page=1, filter_string=''):
    if not filter_string:
        manga_json_response = create_json(api_url_all_manga + str(page), 'all manga')
    else:
        manga_json_response = requests.get(api_url_all_manga + str(page) + filter_string).json()
    catalog_dict = {x['rus_name']: [x['dir'], x['en_name']] for x in manga_json_response['content']}
    return catalog_dict

def get_search_catalog(query_string, count=5):
    encode = urllib.parse.quote(query_string.encode('utf-8'))
    response = requests.get(f'{api_url_search}{encode}&count={str(count)}').json()
    search_catalog_dict = {x['rus_name']: [x['dir'], x['en_name']] for x in response['content']}
    return search_catalog_dict


def view_manga_page(manga_dir, manga_name):
    if '/' in manga_name:
        temp = manga_name.split('/')
        manga_name = temp[0] + temp[1]
    manga_page = create_json(api_url_get_manga + manga_dir, manga_name, manga_dir, False)
    br = max(manga_page['content']['branches'], key=lambda x: x['count_chapters'])
    count_chapters = br['count_chapters']
    page = 1
    while True:
        branch_manga = create_json(f"{api_url_get_manga_branch}{br['id']}&page={page}", 'branch', manga_dir)
        page += 1
        if len(branch_manga['content']) >= count_chapters:
            break
    branch_list = []
    for i in branch_manga['content']:
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
    chapter_response = create_json(api_url_get_manga_chapters + id, name, path_dir, False)
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

