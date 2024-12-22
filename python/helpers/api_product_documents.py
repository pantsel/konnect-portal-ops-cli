import os
import re
from typing import Any, Dict
import utils

def parse_directory(directory: str) -> Dict[str, Any]:
    """Parse the local directory to generate pages with parent-child relationships."""
    
    def extract_sort_key(file_path):
        # Extracts sorting key from file name, e.g., "1.2_filename.md" -> (1, 2)
        match = re.match(r'^(\d+)(?:\.(\d+))?', os.path.basename(file_path))
        return (int(match.group(1)), int(match.group(2)) if match and match.group(2) else 0) if match else (float('inf'), 0)

    parent_pages, pages = {}, []
    # Walk through the directory and sort markdown files by the extracted sort key
    for file_path in sorted((os.path.join(root, file) for root, _, files in os.walk(directory) for file in files if file.endswith('.md')), key=extract_sort_key):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()  # Read and strip content of the file
        
        file_name = os.path.basename(file_path)  # Get the file name
        # Remove '__unpublished' and replace underscores with spaces, capitalize the title
        title_with_numbers = os.path.splitext(file_name)[0].replace('__unpublished', '').replace('_', ' ').capitalize()
        # Remove leading numbers from the title
        title = re.sub(r'^\d+(?:\.\d+)?\s*', '', title_with_numbers).capitalize()
        
        match = re.match(r'^(\d+)(?:\.(\d+))?', file_name)  # Match leading numbers
        # Create slug prefix from matched numbers, e.g., "1.2_filename.md" -> "1-2"
        slug_prefix = match.group(0).replace('.', '-') if match else ''
        # Generate slug using the prefix and slugified title
        slug = slug_prefix + '-' + utils.slugify(title)
        # Determine parent slug if the file represents a child page
        parent_slug = parent_pages.get(match.group(1)) if match and match.group(2) else None
        
        # If the file is a parent page, store its slug
        if match and not match.group(2):
            parent_pages[match.group(1)] = slug
        
        # Append the page information to the pages list
        pages.append({
            "slug": slug.lstrip('-'),  # Cleanup: Remove leading '-' if exists. This is to handle cases where there is no leading number.
            "title": title.title(), 
            "content": utils.encode_content(content), 
            "status": "unpublished" if "__unpublished" in file_name else "published",
            "parent_slug": parent_slug
        })
    
    return pages  # Return the list of pages with their metadata