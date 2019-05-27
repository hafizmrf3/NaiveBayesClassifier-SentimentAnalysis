from django.contrib import admin
from .models import Post, Result, Tweet
from django.contrib.admin import AdminSite
from django.utils.translation import ugettext_lazy

class MyAdminSite(AdminSite):
    # Text to put at the end of each page's <title>.
    site_title = ugettext_lazy('My site admin')

    # Text to put in each page's <h1> (and above login form).
    site_header = ugettext_lazy('My administration')

    # Text to put at the top of the admin index page.
    index_title = ugettext_lazy('Site administration')

admin_site = MyAdminSite()

class ResultAdmin(admin.ModelAdmin):
    list_display = ['sentiment', 'classification']
    list_filter = ()
    search_fields = ['sentiment']
    list_per_page = 25

admin.site.register(Result, ResultAdmin)

class TweetsAdmin(admin.ModelAdmin):
    list_display = ['created_date', 'tweet_text']
    list_filter = ()
    search_fields = ['tweet_text']
    list_per_page = 25

admin.site.register(Tweet, TweetsAdmin)



