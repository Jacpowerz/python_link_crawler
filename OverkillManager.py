import os
import shutil
import TreeHandler as th
import gc
from time import sleep
import psutil

class OverkillManager:
	
	def __init__(self, crawler):
		self.crawler = crawler
		self.tree_name = th.get_root(self.crawler.tree)
		self.base_dir = os.getcwd()
		self.overkill_check = True
	
	def name_handler(self, string):
		if "/" in string: 
			return string.replace("/","!")
		else:
			return string.replace("!","/")
		
	def path_creation_handler(self, my_path):
		if os.path.exists(my_path):
			shutil.rmtree(my_path)
		else:
			os.makedirs(my_path)

	def initialize_paths(self):
		print("initialize path")
		self.data_path = os.path.join(self.base_dir, "data")
		self.tree_path = os.path.join(self.data_path, self.name_handler(self.tree_name))
		self.path_creation_handler(self.data_path)
		self.path_creation_handler(self.tree_path)
		print("init done")

	def activate_overkill(self):
		print("activate overkill")
		self.initialize_paths()
		print(self.tree_name)
		self.crawler.save_tree(self.name_handler(self.tree_name), 1)
		shutil.move(self.name_handler(self.tree_name)+".json", self.tree_path)
		self.clear_ram(self.tree_name)
		
	def process_subtree(self, file_name, remaining_depth):
		print("process subtree")
		fixed_file_name = self.name_handler(file_name)
		json_file_path = os.path.join(self.tree_path, fixed_file_name+".json")
		
		if os.path.exists(json_file_path):
			self.crawler.tree = th.json_to_tree(json_file_path)
		else:
			self.crawler.clear_data(file_name)  # root node
			
		self.crawler.crawl(1,verbose=False)
		self.leaves = th.get_leaves(self.crawler.tree)
		self.crawler.save_tree(fixed_file_name, 1)
		shutil.move(fixed_file_name+".json",json_file_path)
		self.clear_ram(file_name)

	def run(self, remaining_depth, leaves):
		self.leaves = leaves
		self.activate_overkill()
		print("starting overkill search")
		for leaf in self.leaves[1:]:
			self.process_subtree(leaf, remaining_depth)
			
	def clear_ram(self, seed):
		print(f'Ram before: {psutil.virtual_memory()[2]}')
		self.crawler.clear_data(seed)
		print(f'Ram after: {psutil.virtual_memory()[2]}')
