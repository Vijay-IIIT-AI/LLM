data = {
    "Tree Depth 0": ["Main Page", None, None, None, None, None, None, None, None, None, None, None, None, None, None],
    "Tree Depth 1": [None, "0.1 Page 1", None, None, None, "0.2 Page 2", None, None, None, None, None, None, None, None, None],
    "Tree Depth 2": [None, None, "0.1 Page 1.1", "0.2 Page 1.2", None, None, "0.1 Page 2.1", "0.2 Page 2.2", "0.3 Page 2.3", None, None, None, None, None, None],
    "Tree Depth 3": [None, None, None, None, "0.1 Page 1.1.1", None, None, None, None, "0.1 Page 2.3.1", "0.2 Page 2.3.2", None, None, None, "0.3 Page 2.3.3"],
    "Tree Depth 4": [None, None, None, None, None, None, None, None, None, None, None, "0.1 Page 2.3.2.1", "0.1 Page 2.3.2.2", "0.1 Page 2.3.2.3", None]
}

def build_tree(data):
    # Extract levels and initialize the tree
    levels = list(data.values())
    tree = {}

    # Recursive function to build the tree
    def add_to_tree(parent, current_depth, index):
        if current_depth >= len(levels):
            return

        current_level = levels[current_depth]
        for i in range(index, len(current_level)):
            if current_level[i] is not None:
                # Add this node to the parent's dictionary
                parent[current_level[i]] = {}
                # Recur for the next depth level
                add_to_tree(parent[current_level[i]], current_depth + 1, i)

    # Start building the tree from the root
    add_to_tree(tree, 0, 0)
    return tree

def build_paths(data):
    levels = list(data.values())
    paths = []

    def dfs(path, current_depth, index):
        if current_depth >= len(levels):
            return

        current_level = levels[current_depth]
        for i in range(index, len(current_level)):
            if current_level[i] is not None:
                new_path = path + [current_level[i]]
                paths.append(new_path)
                dfs(new_path, current_depth + 1, i)

    dfs([], 0, 0)
    return paths

# Build and display the tree
nested_tree = build_tree(data)
import json
print(json.dumps(nested_tree, indent=4))

# Build and display paths
paths = build_paths(data)


# Create a DataFrame
import pandas as pd
df = pd.DataFrame({"Paths": paths})

