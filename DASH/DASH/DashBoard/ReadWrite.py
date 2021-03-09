import glob
import os
import json


class ReadWrite:
    def __init__(self):
        with open(os.getcwd() + '\\path.json', 'rb') as f:
            self.path = json.load(f)
        self.data = ''

    def returnData(self, file_name):
        self.data = [file for file in glob.glob(self.path['path'] + '*') if file.endswith(file_name + '.pkl')][0]
        return self.data



