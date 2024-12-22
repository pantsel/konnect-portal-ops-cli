import pytest
from src.helpers.api_product_documents import get_slug_tail, parse_directory
from src.helpers.utils import encode_content

@pytest.fixture
def docs_directory(tmpdir):
    # Create a temporary directory structure for testing
    docs_dir = tmpdir.mkdir("docs")
    
    # Create test files
    file1 = docs_dir.join("1_file1.md")
    file1.write("Content of file1")

    file11 = docs_dir.join("1.1_file11.md")
    file11.write("Content of file11")

    file12 = docs_dir.join("1.2_file12.md")
    file12.write("Content of file12")

    file2 = docs_dir.join("2_file2__unpublished.md")
    file2.write("Content of file2")

    return str(docs_dir)

def test_parse_directory(docs_directory):
    pages = parse_directory(docs_directory)

    expected_pages = [{
        "slug": "1-file1",
        "title": "File1",
        "content": encode_content("Content of file1"),
        "status": "published",
        "parent_slug": None
    }, {
        "slug": "1-1-file11",
        "title": "File11",
        "content": encode_content("Content of file11"),
        "status": "published",
        "parent_slug": "1-file1"
    }, {
        "slug": "1-2-file12",
        "title": "File12",
        "content": encode_content("Content of file12"),
        "status": "published",
        "parent_slug": "1-file1"
    }, {
        "slug": "2-file2",
        "title": "File2",
        "content": encode_content("Content of file2"),
        "status": "unpublished",
        "parent_slug": None
    }]

    assert pages == expected_pages

def test_get_slug_tail_single_segment():
    slug = "doc_slug"
    result = get_slug_tail(slug)
    assert result == "doc_slug"

def test_get_slug_tail_multiple_segments():
    slug = "parent_doc_slug/doc_slug"
    result = get_slug_tail(slug)
    assert result == "doc_slug"

def test_get_slug_tail_trailing_slash():
    slug = "parent_doc_slug/doc_slug/"
    result = get_slug_tail(slug)
    assert result == ""

def test_get_slug_tail_empty_slug():
    slug = ""
    result = get_slug_tail(slug)
    assert result == ""

def test_get_slug_tail_no_slash():
    slug = "doc_slug"
    result = get_slug_tail(slug)
    assert result == "doc_slug"

def test_get_slug_tail_leading_slash():
    slug = "/doc_slug"
    result = get_slug_tail(slug)
    assert result == "doc_slug"

def test_get_slug_tail_multiple_slashes():
    slug = "parent_doc_slug/sub_parent/doc_slug"
    result = get_slug_tail(slug)
    assert result == "doc_slug"