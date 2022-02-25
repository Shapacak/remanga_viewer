import requests, json
from pprint import pprint
from PIL.ImageQt import ImageQt
from PIL import Image
from io import BytesIO


class MangaCatalog:
    _url_catalog = 'https://api.remanga.org/api/search/catalog/?ordering=-rating&count=30&page='
    def __init__(self):
        self.filters = ''
        self.page = 1
        self.catalog_list = []

    def initCatalog(self):
        response = requests.get(MangaCatalog._url_catalog).json()
        for i in response['content']:
            page = MangaPage(i)
            self.catalog_list.append(page)

    def getCatalog(self):
        return self.catalog_list

    def filtredCatalog(self):
        pass


class MangaPage:
    _url_page = 'https://api.remanga.org/api/titles/'
    def __init__(self, page_info_dict):
        self.url_directory = page_info_dict['dir']
        self.branch = None
        self.name = page_info_dict['rus_name']
        self.description = ''
        self.img_url = ''

    def initPage(self):
        response = requests.get(MangaPage._url_page + self.url_directory).json()
        self.description = response['content']['description']
        self.img_url = response['content']['img']['high']
        self.branch = Branch(max(response['content']['branches'], key=lambda x: x['count_chapters']))


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
