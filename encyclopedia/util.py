import re

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.files import File # BBG test


def list_entries():
    """
    Returns a list of all names of encyclopedia entries.
    """
    _, filenames = default_storage.listdir("entries")
    return list(sorted(re.sub(r"\.md$", "", filename)
                for filename in filenames if filename.endswith(".md")))


def save_entry(title, content):
	"""
	Saves an encyclopedia entry, given its title and Markdown
	content. If an existing entry with the same title already exists,
	it is replaced.
	
	The ContentFile is a subclass of cStringIO.StringIO - which deals 
	with ASCII encoded files. The string therefore needs to be encoded 
	as ASCII as everything in django is UTF8 by default.
	
	As a result, ContentFile adds extra line spaces during the
	conversion.  To fix this, I added *.encode('ascii').
	Solution:
	https://stackoverflow.com/questions/62903909/django-contentfile-unexpected-empty-line-django-core-files-base
	"""
	filename = f"entries/{title}.md"
	if default_storage.exists(filename):
		default_storage.delete(filename)
	default_storage.save(filename, ContentFile(content.encode('ascii')))


def get_entry(title):
    """
    Retrieves an encyclopedia entry by its title. If no such
    entry exists, the function returns None.
    """
    try:
        f = default_storage.open(f"entries/{title}.md")
        return f.read().decode("utf-8")
    except FileNotFoundError:
        return None
		
def get_substring_entries(title):
	"""
	BBG created to search for entries that contain the
	'title' input as a substring.  
	
	Change both search string and filenames to lower case when trying
	to find a match.
	
	Return a list of matching entries
	"""
	_, filenames = default_storage.listdir("entries")
	return list(sorted(re.sub(r"\.md$", "", filename) 
                for filename in filenames if title.lower() in filename.lower()))
	
