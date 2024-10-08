# All errors and debug messages will be found in 'crawler.log'
import gevent.monkey
gevent.monkey.patch_all()
from requests.packages.urllib3.util.ssl_ import create_urllib3_context
create_urllib3_context()
# The above code must happen before anything else
# It fixes a 'grequests' issue

from treelib import Node, Tree
import requests
from requests.exceptions import RequestException
from bs4 import BeautifulSoup
import re
from collections import deque
import TreeHandler
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(filename='crawler.log', filemode='w', encoding='utf-8', level=logging.INFO)

class Crawler:
	
	def __init__(self, seed):
		if seed[-1] == "/": seed = seed[:-1]
		self.seed = seed
		self.tree = Tree()
		self.tree.create_node(seed, seed)
		self.https_regex = re.compile(r"^https?://")
		self.relative_regex = re.compile(r"^/")
		self.report = "NO DATA"
	
	def display_tree(self, verbose=True):
		if verbose: print(self.tree.show(stdout=False))
		return self.tree.show(stdout=False)
		
	def fetch_links(self, url):
		try:
			response = requests.get(url)
			soup = BeautifulSoup(response.text, 'html.parser')
			a_tags = soup.find_all('a')
			links = set()
			
			for tag in a_tags:
				link = tag.get('href')
				if link:
					if link[-1] == "/": link = link[:-1]
					if self.https_regex.match(link):
						links.add(link)
					elif self.relative_regex.match(link):
						links.add(url + link)
		
			if filter_func: links = filter(filter_func, links)
				
			return links
		
		except RequestException as e:
			logger.info(f"Error occured: {e}")
			return set()

	def add_children(self, links, parent_node):
		for link in links:
			if not self.tree.contains(link):
				self.tree.create_node(link, link, parent_node)
	
	def search_stage1(self):
		leaves = deque(node for node in self.tree.leaves())
			
		if len(leaves) == 1:
			floor = [next(iter(leaves)).identifier]
			next_floor = deque()
		else:
			min_depth = self.tree.depth()
			for leaf in leaves:
				level = self.tree.depth(leaf)
				if level < min_depth:
					min_depth = level
			
			floor = deque(node.identifier for node in leaves if self.tree.depth(node)==min_depth)
			next_floor = deque(node.identifier for node in leaves if self.tree.depth(node)==min_depth+1)
		return floor, next_floor
		
	def search(self, depth, verbose, function):
		
		floor, next_floor = self.search_stage1()
		
		for d in range(depth):
			for child in floor:
				if verbose: print(f"Pending Link: {child}\n")
				childs = self.fetch_links(child, include_relative, include_external)
				self.add_children(childs, child)
				if verbose: print(f"\nLinks added: {len(childs)}")
				
				next_floor.extend(childs)
			floor = next_floor
			next_floor = deque()
			
	def generate_report(self, verbose=True, include_tree=True):
		
		self.report = ""
		if include_tree: self.report += self.display_tree(False)
		
		self.report += f"Links found: {self.tree.size()-1}\n"
		self.report += f"Max Depth: {self.tree.depth()}"
		
		if verbose: print(self.report)

	def save_tree(self, filename, mode=0): 
		if mode == 0:
			self.tree.save2file(filename + ".txt")
		elif mode == 1:
			with(open(filename+".json", "w")) as f:
				f.write(self.tree.to_json())
		elif mode == 2:
			with(open(filename+".txt", "w")) as f:
				for link in sorted(self.tree.all_nodes_itr()):
					f.write(link.identifier + "\n")

	def crawl(self, depth, verbose=True, filter_func=None, overkill_check=True):
		try:
			self.search(depth, verbose, filter_func)
		except KeyboardInterrupt:
			print("You ended the crawl.\n")
			logger.info("You ended the crawl.\n")
		except Exception as e:
			logger.critical(f'Fatal error occured. Error: -->  {e}  <--')
