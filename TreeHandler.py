import json
from treelib import Tree, Node

def json_to_dict(json_file):
	with(open(json_file, "r")) as f:
		data = json.loads(f.read())
	return data

def dict_to_tree(data, parent=None, tree=Tree()):
	for key, value in data.items():
		if key == "children":
			for stuff in value:
				if isinstance(stuff, dict):
					dict_to_tree(stuff, parent, tree)
				else:
					tree.create_node(stuff, stuff, parent)
		else:
			if parent is None:
				tree.create_node(key, key)
			else:
				tree.create_node(key, key, parent)
			parent = key
			dict_to_tree(value, parent, tree)
	return tree

def json_to_tree(json_file):
	data = json_to_dict(json_file)
	return dict_to_tree(data)
