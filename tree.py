import sys
import pprint

# print 'arguments:', sys.argv

# parse the file
filepath = sys.argv[1]

with open(filepath, 'rb') as fh:
    craft = fh.readlines()


unique_parts = {}
    
linecount = 0
node_stack = []
nodes = []

this_container = 'root'
this_uid = ''
for line in craft:
    linecount += 1
    line = line.strip('\r\n\t')
    open_block = '{' in line
    close_block = '}' in line
    key = None
    value = None
    if not (open_block or close_block):
        parts = line.split(' = ', 1)
        key = parts[0]
        if len(parts) == 2:
            value = parts[1]
        else:
            value = None
    
    if key and (value is not None):
        nodes.append([key, value])
        if key == 'part':
            this_uid = value
            unique_parts.setdefault(value)
        if key == 'link':
            unique_parts[value] = this_uid
        
    if key and (value is None) and not open_block and not close_block:
        node_stack.append((nodes, this_container))
        nodes = []
        this_container = key
        # print 'block opened:', len(node_stack), line
    
    if close_block:
        resume_node, resume_container = node_stack.pop()
        resume_node.append([this_container, nodes])
        nodes = resume_node
        this_container = resume_container
        # print 'block closed:', len(node_stack), line

nodes.extend(node_stack)

root_node = [k for k,v in unique_parts.items() if not v]
print 'current root is', root_node
pprint.pprint(unique_parts)

target_node = sys.argv[2]
assert(unique_parts.get(target_node))
# print 'target root is', target_node

# make anyone I was pointing to, now point at me (only one, as it's a tree)
# anyone that was pointing at me, still points at me
def find_links(unique_parts, target_node):
    results = []
    link = unique_parts.get(target_node, None)
    results.append(link)
    if link:
        results.extend(find_links(unique_parts, link))
    return results

new_link_path = [target_node]
new_link_path.extend(find_links(unique_parts, target_node))


new_link_path.pop()
# print new_link_path
new_link_path.reverse()
# print new_link_path
new_link_path.append(None)

# reorder the parent linked list
for i in range(len(new_link_path)-1):
    item = new_link_path[i]
    next_item = new_link_path[i+1]
    unique_parts[item] = next_item

# turn linked list into child map
child_map = {}
for k, v in unique_parts.items():
    child_map.setdefault(v, []).append(k)
  
# pprint.pprint(child_map)   
# pprint.pprint(unique_parts)
# pprint.pprint(nodes)


def make_node_string(lines, nodes, depth):
    pad = '\t' * 1 * depth
    skip = False
    for i in range(len(nodes)):
        if skip:
            skip = False
            continue
        node = nodes[i]
        next_node = nodes[i+1] if (i+1) < len(nodes) else None
        if isinstance(node, list) and isinstance(next_node, list):
            make_node_string(lines, node, depth)
        elif isinstance(next_node, list):
            lines.append("%s%s"%(pad, node))
            lines.append('%s{'%pad)
            make_node_string(lines, next_node, depth+1)
            lines.append('%s}'%pad)
            skip = True
        elif next_node is not None:
            if node == 'link':
                # ignore original links
                continue
            # create the node
            lines.append("%s%s = %s" % (pad, node, next_node))
            if node == 'part':
                # add all the new links
                for child in child_map.get(next_node, []):
                    lines.append("%s%s = %s" % (pad, 'link', child))
        elif isinstance(node, list):
            make_node_string(lines, node, depth)
        else:
            pass
            #lines.append("NEXT NODE IS NONE %s" % node)

lines = []
make_node_string(lines, nodes, 0)

result = '\n'.join(lines)

#print result

with open(filepath+'x', 'wb') as fh:
    fh.write(result)






