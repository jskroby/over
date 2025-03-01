
import os
import graphviz

def generate_diagram():
    """Generate a diagram of the repository structure"""
    # Create text representation
    text_diagram = []
    
    def explore_directory(path, prefix="", is_last=False):
        """Recursively explore directory and generate text diagram"""
        # Get the directory/file name
        name = os.path.basename(path)
        
        # Generate the branch
        branch = "└── " if is_last else "├── "
        
        # Add to text diagram
        text_diagram.append(f"{prefix}{branch}{name}")
        
        # New prefix for children
        child_prefix = prefix + ("    " if is_last else "│   ")
        
        # Get all items in directory
        if os.path.isdir(path):
            items = sorted(os.listdir(path))
            
            # Filter out some common directories/files to keep diagram clean
            items = [item for item in items if item not in [".git", "__pycache__", "node_modules", ".venv"]]
            
            # Process each item
            for i, item in enumerate(items):
                item_path = os.path.join(path, item)
                explore_directory(item_path, child_prefix, i == len(items) - 1)
    
    # Start exploration from current directory
    explore_directory(".", "")
    
    # Write text diagram to file
    with open("repository_diagram.txt", "w") as f:
        f.write("\n".join(text_diagram))
    
    # Create graphviz diagram
    dot = graphviz.Digraph(comment='Repository Structure', format='png')
    dot.attr('node', shape='box', style='filled', fillcolor='lightblue')
    dot.attr('edge', arrowhead='none')
    
    # Map to store nodes
    nodes = {}
    
    def add_to_graph(path, parent=None):
        """Add directory/file to graph"""
        name = os.path.basename(path) or "."
        node_id = path or "."
        
        # Add node if not already added
        if node_id not in nodes:
            is_dir = os.path.isdir(path)
            fillcolor = 'lightblue' if is_dir else 'lightgrey'
            dot.node(node_id, name, fillcolor=fillcolor)
            nodes[node_id] = True
        
        # Add edge from parent to this node
        if parent:
            dot.edge(parent, node_id)
        
        # Recursively add children if directory
        if os.path.isdir(path):
            items = sorted(os.listdir(path))
            items = [item for item in items if item not in [".git", "__pycache__", "node_modules", ".venv"]]
            
            for item in items:
                item_path = os.path.join(path, item)
                add_to_graph(item_path, node_id)
    
    # Start building the graph
    add_to_graph(".")
    
    # Render the graph
    dot.render('repository_diagram', view=False)
    
    print("Repository diagram generated:")
    print("1. Text diagram: repository_diagram.txt")
    print("2. Visual diagram: repository_diagram.png")

if __name__ == "__main__":
    generate_diagram()
