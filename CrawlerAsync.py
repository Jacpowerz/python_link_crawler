import grequests
from Crawler import Crawler, BeautifulSoup, deque

class CrawlerAsync(Crawler):
	
	def fetch_links(self, url, include_relative, include_external, response):

		soup = BeautifulSoup(response.text, 'html.parser')
		a_tags = soup.find_all('a')
		links = set()
			
		for tag in a_tags:
			link = tag.get('href')
			if link:
				if link[-1] == "/": link = link[:-1]
				if include_external and self.https_regex.match(link):
					links.add(link)
				elif include_relative and self.relative_regex.match(link):
					links.add(url + link)
		return links
		
	def search(self, depth, include_relative, include_external, verbose):
		
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
			
		for d in range(depth):
			pending_leaves = (grequests.get(u) for u in floor)
			responses = grequests.imap_enumerated(pending_leaves)
			for index, child in responses:
				child_url = floor[index]
				childs = self.fetch_links(child_url, include_relative, include_external, child)
				self.add_children(childs, child_url)
				
				if verbose:
					print(f"Completed: {child_url}\nLinks added: {len(childs)}")
				
				next_floor.extend(childs)
			floor = next_floor
			next_floor = deque()
