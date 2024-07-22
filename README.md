# Link Spider

## Features

- Async option
- Filter which links can be stored
- In progress: When computer runs out of memory start switch into different mode to save RAM.
     - This works technically but it doesn't help save RAM at all and is just slower.
- Gracefully stops right before ram is fully used up.

## Example

Spiderman = CrawlerAsync(link)\n
Spiderman.crawl(5,verbose=False, overkill_check=True)\n
Spiderman.save_tree(link_new, 2)

This code creates the crawler object and searcehs the link to a depth of 5. verbose is whether it will print info to console and overkill_check is whether it monitors RAM 
and acts accordingly. As of now the code just stops execution, but it was made with the intention of offloading memory usage in exchange for more cpu intensive tasks. Does 
not work at all. The intended code for that is commented out in the 'CrawlerAsync.py' file.
