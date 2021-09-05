from django.shortcuts import render
from django.http import HttpResponse # BBG added
from django import forms # BBG added
from django.urls import reverse # BBG added
from django.http import HttpResponseRedirect # BBG added
from django.core.exceptions import ValidationError # BBG added

from . import util
from markdown2 import Markdown
import random

class EditPageForm(forms.Form):
	"""
	BBG created
	
	Display the content field on the editpage.html.  
	
	Note:
	the content field is already populated with the content via
	an initial value set in the views/editpage function.
	
	
	Tried to use an initialized title and set it to disabled=True,
	to prevent user from changing it, but when the form is submitted
	back to the views/editpage as POST, the title is missing.
	
	Workaround is to use a hidden value in the editpage.html, and
	retrieve that value in the views/editpage.
	"""
	
	# This doesn't work, but leaving in case of brilliant idea
	# Make the title field read-only using the disabled flag
	# title = forms.CharField(
		# widget = forms.TextInput(attrs = {
			# 'class': 'form-control',
			# 'placeholder':'Enter a Title...',
			# }),
		# #disabled = True,
		# required = True)
		
	content = forms.CharField(
		widget=forms.Textarea(attrs = {
			'class': 'form-control',
			'placeholder': 'Enter Markdown Content...',
		}),
		required = True)
	
class NewSearchForm(forms.Form):
	"""
	BBG created

	This class is used for the search feature on the side bar.
	
	CharField is a class, so 'title' is an object.
		https://docs.djangoproject.com/en/3.1/ref/forms/fields/#charfield
		
	'title' will contain the search result the user enters.
	"""
	title = forms.CharField(
		label = 'Search:',
		widget = forms.TextInput(attrs = {
			'placeholder': 'Search...',
			'class': 'form-control'
		}))
	
class NewPageForm(forms.Form):
	"""
	This class handles the title and content entries on the newpage.html page.
	
	In addition, validation is performed on the title for a POST request, to 
	determine if the page already exists.  This is done via the clean_title method.
	If page exists, raise an exception.
	
	Styling information was found here:
		https://youtu.be/_oMY2o2NhWM
	
	Content uses the 'Textarea' widget defined here:
		https://docs.djangoproject.com/en/3.2/ref/forms/widgets/#django.forms.Textarea
	
	ValidationError referenced here:
		https://docs.djangoproject.com/en/3.2/ref/forms/validation/
	"""
	title = forms.CharField(
		widget=forms.TextInput(attrs={
			'class': 'form-control',
			'placeholder':'Enter a Title...',
			}),
		label = 'Enter a title:',
		min_length = 1,
		required = True)
		
	content = forms.CharField(
		widget = forms.Textarea(attrs = {
			'class': 'form-control',
			'placeholder': 'Enter Markdown Content...',
		}),
		required = True)
	
	
	# Method is called when is_valid() is run
	# Could use some work so error is not displayed as a list with the title
	def clean_title(self):
		"""Method to determine if the title is unique"""
		data = self.cleaned_data['title']
		if util.get_entry(data) is not None:
			raise forms.ValidationError('Page already exists. Enter a unique page name.')

		# Always return a value to use as the new cleaned data, even if
		# this method didn't change it.
		return data
		
	
def index(request):
	"""
	This function was provided by the course instructor
	Modified form to be 'search_form'
	"""
	return render(request, "encyclopedia/index.html", {
		"entries": util.list_entries(),
		"search_form": NewSearchForm()
	})


# Should this be a new App?  I thought any page with a / at the end should be a new app?  Not sure though...
def search(request):
	"""
	When user searches for a page,
	--if the page is found, redirect user to the page
	--if the page is not found, show user listings with matching substrings

	"""

	# Check if request method is POST (from the Search Form submission)
	if request.method == 'GET':
		form = NewSearchForm(request.GET)
		
		if form.is_valid():
			# Isolate the title from the 'cleaned version of form data
			title = form.cleaned_data["title"]
			
			# Determine if wiki page exists
			result = util.get_entry(title)
			
			# If page exists, direct user to page
			if result is not None:
				# Redirect user to the URL containing the search string
				# referenced: https://docs.djangoproject.com/en/3.2/intro/tutorial04/ for args
				return HttpResponseRedirect(reverse('encyclopedia:wiki', args=(title,)))
				
			# If page does not exist, direct user to search results containing search string
			else:
				# Get list of entries that contain the substring
				substring_entries = util.get_substring_entries(title)
				
				return render(request, "encyclopedia/search.html", {
					"entries": substring_entries,
					"search_form": NewSearchForm()
				})
		# form is invalid, re-render index page with existing form information
		# This will happen if user just tries to go to /search/ directly
		else:
			return render(request, "encyclopedia/index.html", {
				"entries": util.list_entries(),
				"search_form": form
			})
				
	# Else just redirect user to index page
	# This should never execute
	else:
		# Direct user to page
		return HttpResponseRedirect(reverse('encyclopedia:index'))

def wiki(request, title):
	"""
	BBG created.
	
	This function accepts a variable called title, which is a string.
	
	The function will pass the title variable into the util.get_entry()function.
	
	If get_entry() returns a result other than none, display the result on a 
	webpage.  The title of the page will be the title variable name.
	
	If the result is none, display an error page.
	"""
	result_markdown = util.get_entry(title)
	
	if result_markdown is None:
		result = "The Requested Page Was Not Found."
	else:
		#convert result to HTML
		markdowner = Markdown()
		result = markdowner.convert(result_markdown)
	
	return render(request, "encyclopedia/wiki.html", {
		"title": title,
		"entry": result,
		"search_form": NewSearchForm()
	})

def editpage(request):
	"""
	BBG created.
	
	The function handles the user request to edit a page.  A user can edit a page by
	clicking the edit button on a wiki page entry.
	
	The content is displayed to the user as a form which is pre-populated with the
	current entry.
	
	User can modify the content and save the form.
	"""
	
	# when user clicks button, it should send the title of the page to this method
	# this method should use the title of the page and the render the editpage
	# with the content (retrieved from util.py)
	
	# Execute this code when Edit button is clicked (from a wiki/ page)
	if request.method == 'GET':
		
		# get the hidden title value
		# request.GET.get() was the only way I could figure out how to
		# 	get the hidden value, since it's not a user input.
		title = request.GET.get("title")
		
		# Check if user manually typed in /editpage/ in url by seeing if
		# value of title is None.  If None, then redirect user to index 
		# page.
		if title is None:
			# Direct user to page
			return HttpResponseRedirect(reverse('encyclopedia:index'))
		
		# get the content using the util function 
		content = util.get_entry(title)
		
		# 'initial' information found here: 
		#	https://docs.djangoproject.com/en/3.2/ref/forms/api/#django.forms.Form.initial
		return render(request, "encyclopedia/editpage.html", {
			"search_form": NewSearchForm(),
			"edit_page_form": EditPageForm(initial={'content': content}),
			"title":title
		})
		
	# Execute this code when the Save button is hit
	# request.method == 'POST'
	else:
		form = EditPageForm(request.POST)
		
		if form.is_valid():
			# Isolate the title from the 'cleaned version of form data
			#title = form.cleaned_data["title"]
			title = request.GET.get("title")
			content = form.cleaned_data["content"]
			print(content)
		
			# Save page to disk
			util.save_entry(title, content)
			
			# Direct user to page
			return HttpResponseRedirect(reverse('encyclopedia:wiki', args=(title,)))
	
		# form is invalid, re-render index page with existing form information
		else:
			return render(request, "encyclopedia/editpage.html", {
				"search_form": NewSearchForm(),
				"edit_page_form": form
			})

def newpage(request):
	"""
	BBG created.
	
	This function handles when a user clicks the "Create New Page" link on the sidebar,
	and when the user submits the new page form.
	
	When a user clicks the "Create New Page" link, a form will be displayed to the user
	containing a location to enter the title and description.  This is the GET request.
	
	When a user fills in the new form fields and submits the form:
		- A new entry will be saved to disk if it hasn't been created.
			- User will then be directed to the new page.
		- If entry already exists, an error will be displayed.

	"""
	# Execute this code if a new form is submitted
	if request.method == 'POST':
		form = NewPageForm(request.POST)
		
		if form.is_valid():
			# Isolate the title from the 'cleaned version of form data
			title = form.cleaned_data["title"]
			content = form.cleaned_data["content"]
			
			# Determine if wiki page exists
			result = util.get_entry(title)
			
			# If page exists, direct user to page
			if result is not None:
				# Redirect user to the URL containing the search string
				# referenced: https://docs.djangoproject.com/en/3.2/intro/tutorial04/ for args
				return HttpResponseRedirect(reverse('encyclopedia:wiki', args=(title,)))
				
			# If page does not exist,
			# -- Save page to disk
			# -- Direct user to new page
			else:
				# Save page to disk
				util.save_entry(title, content)
				
				# Direct user to new page
				return HttpResponseRedirect(reverse('encyclopedia:wiki', args=(title,)))
		
		# form is invalid, re-render index page with existing form information
		else:
			return render(request, "encyclopedia/newpage.html", {
				"search_form": NewSearchForm(),
				"new_page_form": form
			})
	
	# Get request method
	else:
		return render(request, "encyclopedia/newpage.html", {
			"search_form": NewSearchForm(),
			"new_page_form": NewPageForm()
		})
	
def randompage(request):
	"""
	This function will select a random encyclopedia entry and
	direct the user to the page on wiki/<page>.
	"""
	# Pull all entries / titles
	entries = util.list_entries()
	
	# Randomly pick an entry / title
	title = random.sample(entries, 1)
	
	# title is a list, so we need first value
	title = title[0]

	# Direct user to new page
	return HttpResponseRedirect(reverse('encyclopedia:wiki', args=(title,)))
	
