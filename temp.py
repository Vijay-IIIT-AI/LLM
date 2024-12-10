# Build the tree_info list based on ancestors and current page
            tree_metadata = []
            
            # Add ancestors first
            for i, ancestor in enumerate(page.ancestors):
                tree_metadata.append(f"Tree Depth {i}: {ancestor['title']}")
            
            # Add the current page
            tree_metadata.append(f"Tree Depth {page.level}: {page.title}")
