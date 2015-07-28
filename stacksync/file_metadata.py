# -*- encoding: utf-8 -*-

import datetime
import time

class FileMetadata:
    def __init__(self, name, date, file_id, is_folder,  size, mimetype, parent_id, modified_at, version):
        self.name = name
        DB_TIME_FORMAT = '%Y-%m-%d %H:%M:%S.%f'
        date_aux = datetime.datetime.fromtimestamp(time.mktime(time.strptime(date, DB_TIME_FORMAT)))
        self.date = date_aux
        self.file_id = file_id
        self.is_folder = is_folder
        self.size = size
        self.mimetype = mimetype
        self.parent_id = parent_id
        self.modified_at = modified_at
        self.version = version


class FileMetadataHelper:

    def __init__(self, formatted_json_content):
        self.json_content = formatted_json_content

    def compute_size(self):
        total_size = 0
        for item in self.json_content['contents']:
            total_size += item['size']

        return total_size

    def create_FileMetadata(self, item):
        fileMetadata = FileMetadata(item['filename'], item['modified_at'], item['id'],
                                item['is_folder'], item['size'], item['mimetype'], item['parent_id'], item['modified_at'],
                                item['version'])
        return fileMetadata

    def filter_metadata_by_type(self, file_list, folder_list):
        """
        Populates two lists, one of files and one of folders

        :param file_list: List of FileMetadata objects, that map to a file type
        :param folder_list: List of FileMetadata objects, that map to a folder type
        :param json_data: input of json formatted data
        :return:
        """
        for item in self.json_content['contents']:
            fileMetadata = self.create_FileMetadata(item)
            if item['is_folder']:
                folder_list.append(fileMetadata)
            else:
                file_list.append(fileMetadata)

    def add_initial_subfolder_metadata(self, folder_list):
        fileMetadata = self.create_FileMetadata(self.json_content)
        folder_list.append(fileMetadata)

