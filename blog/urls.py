from django.conf.urls import url
from django.contrib.auth.views import logout_then_login

from . import views


urlpatterns = [
	url(r'^$', views.home, name='home'),
	url(r'^crawling/$', views.crawling, name='crawling'),
	url(r'^classify/$', views.classify, name='classify'),
	url(r'^tweets/$', views.get_tweets, name='get_tweets'),
	url(r'^about/$', views.about, name='about'),
	url(r'^home/login$', views.login, name='login'),
	url(r'^home/logout$', views.logout_view, name='logout_view'),
	#url(r'^home/logout$', lambda request: logout_then_login(request, "/"), name='logout_view'),
]