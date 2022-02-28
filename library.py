import json
import os.path


class Library:
    def __init__(self):
        super(Library, self).__init__()
        self.lib = {}
        self.initLibrary()

    def initLibrary(self):
        if not os.path.exists('library.json'):
            with open('library.json', 'w', encoding='utf-8') as lib:
                json.dump(self.lib, lib)
        else:
            with open('library.json', 'r', encoding='utf-8') as lib:
                self.lib = json.load(lib)

    def getLibrary(self):
        return self.lib

    def saveLibrary(self):
        with open('library.json', 'w', encoding='utf-8') as lib:
            json.dump(self.lib, lib)

    def addLibrary(self, to_save_list):
        self.lib[to_save_list[0]] = {'rus_name':to_save_list[0], 'dir':to_save_list[1], 'current_chapter':to_save_list[2]}
