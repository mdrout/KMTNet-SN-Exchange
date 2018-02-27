"""kmtshi URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""

from django.conf.urls import url
from django.contrib import admin
from django.contrib.auth import views as auth_views
from kmtshi import views

urlpatterns = [url(r'^$', views.index, name='index'),
               url(r'^login$', auth_views.login,name='login'),
               url(r'^logout$', auth_views.logout,name='logout'),
               url(r'^all-fields/candidates/$', views.candidates, name='candidates'),
               url(r'^(?P<field>[A-Z0-9-]+)/candidates/$', views.candidates_field, name='candidates_field'),
               url(r'^(?P<field>[A-Z0-9-]+)/candidates_form/$', views.candidates_field_form, name='candidates_field_form'),
               url(r'^all-fields/transients/$', views.transients, name='transients'),
               url(r'^(?P<field>[A-Z0-9-]+)/transients/$', views.transients_field, name='transients_field'),
               url(r'^all-fields/galaxies/$', views.galaxies, name='galaxies'),
               url(r'^(?P<field>[A-Z0-9-]+)/galaxies/$', views.galaxies_field, name='galaxies_field'),
               url(r'^all-fields/variables/$', views.variables, name='variables'),
               url(r'^(?P<field>[A-Z0-9-]+)/variables/$', views.variables_field, name='variables_field'),
               url(r'^object/(?P<candidate_id>[0-9]+)/$', views.detail,name='detail'),
               url(r'^object/(?P<candidate_id>[0-9]+)/class_edit/$', views.classification_edit,name='classification_edit'),
               url(r'^(?P<field>[A-Z0-9-]+)/(?P<quadrant>[A-Z0-9]+)/(?P<date>[A-Z0-9_]+)/candidates/$', views.candidate_date,name='candidates_date'),
               url(r'^(?P<field>[A-Z0-9-]+)/(?P<quadrant>[A-Z0-9]+)/(?P<date>[A-Z0-9_]+)/bulk_edit/$', views.classification_bulkedit,name='class_bulkedit'),
               url(r'^name-search/(?P<sname>[a-zA-Z0-9-]+)/$',views.search_name, name='search_name'),
               url(r'^coord-search/ra=(?P<ra>[0-9.-]+);dec=(?P<dec>[0-9.-]+);radius=(?P<radius>[0-9.-]+)/$',views.search_coord, name='search_coord'),
               url(r'^admin/', admin.site.urls)]

