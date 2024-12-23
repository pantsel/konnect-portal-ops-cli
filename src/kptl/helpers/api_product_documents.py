import os
import re
from typing import Any, Dict
from kptl.helpers import utils

def parse_directory(directory: str) -> Dict[str, Any]:
    """
    Parse the directory to generate pages with metadata and parent-child relationships.
    
    File Naming Conventions:
    - Leading numbers indicate order and hierarchy, e.g., "1_filename.md", "1.1_child_filename.md".
    - "__unpublished" suffix indicates unpublished status.
    - Underscores in filenames are replaced with spaces in the title.

    Example Directory Structure:
    /example_directory
    ├── 1_introduction.md
    ├── 1.1_getting_started.md
    ├── 2_features.md
    ├── 2.1_feature_one.md
    ├── 2.2_feature_two__unpublished.md
    └── 3_conclusion.md

    Example Output:
    [
        {"slug": "1-introduction", "title": "Introduction", "content": "<encoded content>", "status": "published", "parent_slug": None},
        {"slug": "1-1-getting-started", "title": "Getting started", "content": "<encoded content>", "status": "published", "parent_slug": "1-introduction"},
        {"slug": "2-features", "title": "Features", "content": "<encoded content>", "status": "published", "parent_slug": None},
        {"slug": "2-1-feature-one", "title": "Feature one", "content": "<encoded content>", "status": "published", "parent_slug": "2-features"},
        {"slug": "2-2-feature-two", "title": "Feature two", "content": "<encoded content>", "status": "unpublished", "parent_slug": "2-features"},
        {"slug": "3-conclusion", "title": "Conclusion", "content": "<encoded content>", "status": "published", "parent_slug": None}
    ]

    Args:
        directory (str): Path to the directory containing markdown files.
    Returns:
        Dict[str, Any]: List of dictionaries, each representing a page with its metadata.
    """
    
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


def get_slug_tail(slug: str) -> str:
    """
    Extracts the tail part of the given slug.

    This method is needed because the Konnect API's list document operation 
    returns a slug in the format of parent_doc_slug/doc_slug, depending on 
    whether the document has a parent. This occurs regardless of whether 
    only the doc_slug was specified when creating the document.

    Args:
        remote_page (dict): A dictionary representing the remote page, which
                            contains a 'slug' key with the URL path as its value.

    Returns:
        str: The last segment of the slug URL path.
    """
    return slug.split('/')[-1]