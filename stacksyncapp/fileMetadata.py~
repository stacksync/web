import datetime
import time

class FileMetadata:
	def __init__(self, name, date, file_id, is_folder, path, size, mimetype):        
		self.name = name
		DB_TIME_FORMAT = '%Y-%m-%d %H:%M:%S.%f'
		dateAux = datetime.datetime.fromtimestamp(time.mktime(time.strptime(date, DB_TIME_FORMAT)))
		self.date = dateAux
		self.file_id = file_id
		self.is_folder = is_folder
		self.path = path
		self.size = size
		self.mimetype = mimetype
