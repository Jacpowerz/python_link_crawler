import grequests
from Crawler import Crawler, BeautifulSoup, deque, logger, Tree

import resource
resource.setrlimit(resource.RLIMIT_NOFILE, (100_000, 100_000))
# The above two lines should fix 'too many open files' error

import psutil
import signal
import os
from OverkillManager import OverkillManager
import TreeHandler as th

def exception_handler(request, exception):
	logger.error(f'grequests error occured. Error: -->  {exception}  <--')

class CrawlerAsync(Crawler):

	def __init__(self, url, timeout=None, manager=None):
		super().__init__(url)
		self.timeout = timeout
		if not manager: 
			self.manager = OverkillManager(self)
		else:
			self.manager = manager
	
	def fetch_links(self, url, response, filter_func):

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
		
	def overkill_check(self, depth, cur_depth):
		ram_usage = psutil.virtual_memory()[2]
		ram_limit = 90
		if ram_usage > ram_limit:
			'''
			self.manager.overkill_check = False
			logger.info(f'Memory limit ({ram_limit}%) exceeded. Overkill enabled')
			self.manager.run(depth-cur_depth, th.get_leaves(self.tree))
			logger.info("Overkill manager finished search")
			print("search complete")
			'''
			os.kill(os.getpid(), signal.SIGINT)

	def search(self, depth, verbose, filter_func):
		
		floor, next_floor = self.search_stage1()
			
		for d in range(depth):
			pending_leaves = (grequests.get(u) for u in floor)
			responses = grequests.imap_enumerated(pending_leaves, exception_handler=exception_handler)
			for index, child in responses:
				child_url = floor[index]
				try:
					childs = self.fetch_links(child_url, child, filter_func)
					self.add_children(childs, child_url)
					
					if verbose: print(f"Completed: {child_url}\nLinks added: {len(childs)}")
					
					next_floor.extend(childs)
					
					if self.manager.overkill_check: self.overkill_check(depth, self.tree.depth())
						
				except Exception as e:
					logger.error(f'Could not add children for {child_url} due to Error: -->  {e}  <--')
					
			floor = next_floor
			next_floor = deque()
			
	def clear_data(self, seed):
		self.seed = seed
		self.tree = Tree()
		self.tree.create_node(seed, seed)
		
