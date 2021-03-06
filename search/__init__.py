
import fman.fs
import sys,os,time, datetime,locale,re
from fman.fs import FileSystem
from core.quicksearch_matchers import contains_chars
from fman import DirectoryPaneCommand, show_alert, show_prompt, show_quicksearch, QuicksearchItem, show_status_message, clear_status_message
from fman.url import splitscheme, as_url, join, basename, as_human_readable, dirname
from fman.impl.util.qt.thread import run_in_main_thread
from core.tests import StubFS
from gui.searchdialog import SearchDialog
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QMessageBox
from searcher.directory_node import DirectoryNode
from stat import *
from datetime import datetime
from io import UnsupportedOperation

root_node = DirectoryNode()

class SearchWithDialog(DirectoryPaneCommand):
	@run_in_main_thread
	def __call__(self):
		scheme, currentDir = splitscheme(self.pane.get_path())
		currentDir = os.path.normpath(currentDir)
		
		global current_dir
		global current_parent_dir
		
		current_dir = currentDir
		current_parent_dir = os.path.normpath(os.path.join(current_dir, os.pardir))
		
		
		self.searchDialog = SearchDialog(scheme,currentDir,self.pane,root_node)
		self.searchDialog.show()


class SearchFileSystem(FileSystem):
	scheme = 'search://'

	def __init__(self, fs=fman.fs, suffixes=None):
		super().__init__()
		self._fs = fs
		self._suffixes = suffixes

	def get_default_columns(self, path):
		return 'core.Name', 'core.Size', 'core.Modified'

	def resolve(self, path):
	
		if current_parent_dir == os.path.normpath(path):
			return as_url(current_dir)
		
		return super().resolve(path)
			

	def iterdir(self, path):
		list = []
		
		if path == '':
			list = root_node.children_as_string
		else:
			node = root_node.get_from_os_path(path)
			if not node is None:
				list = node.children_as_string
			
		return(list)

	def is_dir(self, path):
		try:
			node = root_node.get_from_os_path(path)
			filestat = node.os_filestat
			mode = filestat.st_mode
			return(S_ISDIR(mode))
		except Exception as e:
			return(False)


	def size_bytes(self, path):
		node = root_node.get_from_os_path(path)
		filestat = node.os_filestat
		return(filestat.st_size)

	def modified_datetime(self, path):
		node = root_node.get_from_os_path(path)
		filestat = node.os_filestat
		return datetime.fromtimestamp(filestat.st_mtime)

	def copy(self, src_url, dst_url):
		src_scheme, src_path = splitscheme(src_url)

		file_scheme = 'file://'

		if src_scheme == self.scheme and dst_scheme == file_scheme:
			fman.fs.copy(as_url(src_path,file_scheme), dst_url)
		else:
			raise UnsupportedOperation()

	def move(self, src_url, dst_url):
		raise UnsupportedOperation()

	def mkdir(self, path):
		raise UnsupportedOperation()

	def delete(self, path):
		raise UnsupportedOperation()



