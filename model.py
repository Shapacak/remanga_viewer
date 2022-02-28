import requests, json
from pprint import pprint
from PIL.ImageQt import ImageQt
from PIL import Image
from io import BytesIO
import urllib.parse


class MangaCatalog:
    _url_catalog = 'https://api.remanga.org/api/search/catalog/?count=30&page='
    _url_search = 'https://api.remanga.org/api/search/?query='
    def __init__(self):
        self.filters = Filter()
        self.ordering = Ordering()
        self.page = 1
        self.catalog_list = []
        self.search_catalog = []
        self.lib_catalog = []

    def initCatalog(self):
        response = requests.get(MangaCatalog._url_catalog+str(self.page)+self.ordering.getOrderingString()+self.filters.getFilterString()).json()
        for i in response['content']:
            page = MangaPage(i)
            self.catalog_list.append(page)

    def initSearchCatalog(self, search_string, count=5):
        self.search_catalog = []
        encode_string = urllib.parse.quote(search_string.encode('utf-8'))
        response = requests.get(MangaCatalog._url_search + encode_string + f'&count={str(count)}').json()
        for i in response['content']:
            page = MangaPage(i)
            self.search_catalog.append(page)

    def initLibCatalog(self, lib_list):
        for k, v in lib_list.items():
            page = MangaPage(v)
            self.lib_catalog.append(page)

    def clearCatalog(self):
        self.catalog_list = []

    def nextPage(self):
        self.page += 1

    def firstPage(self):
        self.page = 1

    def getSearchCatalog(self):
        return self.search_catalog

    def getCatalog(self):
        return self.catalog_list

    def getLibCatalog(self):
        return self.lib_catalog



class Filter:
    _url_filters = 'https://api.remanga.org/api/forms/titles/?get=genres&get=categories&get=types&get=status&get=age_limit'
    _rep_names = {'genres': 'Жанры', 'categories': 'Категории',
                 'types': 'Типы', 'status': 'Статус', 'age_limit': 'Возрастные ограничения'}
    def __init__(self):
        self.filter_string = ''
        self.all_filters_data = {}
        self.initFilters()

    def initFilters(self):
        response_all_filters = requests.get(Filter._url_filters).json()
        for k in response_all_filters['content']:
            if k in Filter._rep_names:
                self.all_filters_data[Filter._rep_names[k]] = response_all_filters['content'][k]


    def buildFilterString(self, filters_list):
        if filters_list:
            inv_names = {v:k for k,v in Filter._rep_names.items()}
            filter_string = ''
            for filter in filters_list:
                    filter_string = filter_string + f'&{inv_names[filter[0]]}={filter[1]}'
            self.filter_string = filter_string
        else:
            self.filter_string = ''

    def getFilterString(self):
        return self.filter_string

    def getAllFilters(self):
        return self.all_filters_data


class Ordering:
    _ordering = {'id': 'По новизне', 'chapter_date': 'По последним обновлениям', 'rating': 'По популярности',
                         'votes': 'По лайкам', 'views': 'По просмотрам', 'count_chapters': 'По колличеству глав',
                         'random': 'Случайно'}
    def __init__(self):
        self.ordering_string = '&ordering=-rating'

    def buildOrderingString(self, ordering_list):
        if ordering_list:
            ordering_string = ''
            for i in ordering_list:
                ordering_string = ordering_string + f'&ordering=-{i}'
            self.ordering_string = ordering_string
        else:
            self.ordering_string = '&ordering=-rating'

    def getOrderingString(self):
        return self.ordering_string

    def getAllOrdering(self):
        return Ordering._ordering


class MangaPage:
    _url_page = 'https://api.remanga.org/api/titles/'
    _url_img = 'https://remanga.org'
    def __init__(self, page_info_dict):
        self.url_directory = page_info_dict['dir']
        self.branch = None
        self.name = page_info_dict['rus_name']
        self.description = ''
        self.img_url = ''

    def initPage(self):
        response = requests.get(MangaPage._url_page + self.url_directory).json()
        self.description = response['content']['description']
        self.branch = Branch(max(response['content']['branches'], key=lambda x: x['count_chapters']))
        self.img_url = response['content']['img']['high']

    def loadPageImg(self):
        response = requests.get(MangaPage._url_img + self.img_url, stream=True)
        im = Image.open(BytesIO(response.content))
        image = ImageQt(im)
        return image

    def addToLibrary(self):
        return [self.name, self.url_directory]


class Branch:
    _url_branch = 'https://api.remanga.org/api/titles/chapters/?ordering=index&count=60&branch_id='
    def __init__(self, list_branch):
        self.branch_id = str(list_branch['id'])
        self.count_chapters = list_branch['count_chapters']
        self.chapters_list = []


    def initBranch(self):
        response = requests.get(Branch._url_branch+self.branch_id).json()
        for i in response['content']:
            self.appendChapter(i)

    def appendChapter(self, data):
        if self.chapters_list == []:
            chapter = Chapter(data)
            self.chapters_list.append(chapter)
        else:
            n = self.chapters_list[-1]
            chapter = Chapter(data)
            n.next_chapter = chapter
            chapter.previous_chapter = n
            self.chapters_list.append(chapter)

    def getBranch(self):
        return self.chapters_list

    def getChapter(self, index):
        return self.chapters_list[index]

class Chapter:
    _url_chapter = 'https://api.remanga.org/api/titles/chapters/'
    def __init__(self, chapter_info_dict):
        self.id = str(chapter_info_dict['id'])
        self.name = chapter_info_dict['name']
        self.chapter = str(chapter_info_dict['chapter'])
        self.tome = str(chapter_info_dict['tome'])
        self.next_chapter = None
        self.previous_chapter = None
        self.frames_list = []

    def initChapter(self):
        response = requests.get(Chapter._url_chapter + self.id).json()
        if response['content']['is_paid'] == False:
            for i in response['content']['pages']:
                frame = Frame(i)
                self.frames_list.append(frame)

    def nextChapter(self):
        if self.next_chapter:
            return self.next_chapter
        else:
            return

    def previousChapter(self):
        if self.previous_chapter:
            return self.previous_chapter
        else:
            return

    def getFrames(self):
        return self.frames_list

    def addToLibrary(self):
        return self.id

class Frame:
    def __init__(self, frame_info):
        if type(frame_info) is list:
            self.getFrameWithList(frame_info)
        else:
            self.getFrame(frame_info)


    def getFrame(self, frame_info):
        response = requests.get(frame_info['link'], stream=True)
        im = Image.open(BytesIO(response.content))
        self.image = ImageQt(im)
        return self.image

    def getFrameWithList(self, frame_info):
        parts = []
        for part in frame_info:
            response_img = requests.get(part['link'])
            img = Image.open(BytesIO(response_img.content))
            parts.append(img)
        widths, heights = zip(*(i.size for i in parts))

        total_width = max(widths)
        max_height = sum(heights)

        new_im = Image.new('RGB', (total_width, max_height))

        y_offset = 0
        for im in parts:
            new_im.paste(im, (0, y_offset))
            y_offset += im.size[1]

        self.image = ImageQt(new_im)
        return self.image
