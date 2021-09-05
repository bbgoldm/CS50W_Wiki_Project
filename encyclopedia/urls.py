from django.urls import path

from . import views

# Need to add 'app_name' to avoid collisions
app_name = "encyclopedia"
urlpatterns = [
    path("", views.index, name="index"),
	path('wiki/', views.index, name="index"),  # BBG added, this is optional
	path('wiki/<str:title>', views.wiki, name="wiki"), # BBG added
	path('search/', views.search, name="search"), # BBG added for when user searches
	path('newpage/', views.newpage, name="newpage"), # BBG added for user to create new page
	path('editpage/', views.editpage, name="editpage"), # BBG added for user to edit existing page
	path('randompage/', views.randompage, name="randompage") # BBG added when user clicks random page button
]
