from django.contrib.sitemaps import Sitemap
from django.core.cache import cache
from django.core.paginator import Paginator
from django.urls import reverse

class HomeSitemap(Sitemap):
    changefreq = "weekly"
    priority = 1.0
    protocol = "https"

    def items(self):
        return ['baseapp:home']

    def location(self, item):
        return reverse(item)


sitemaps = {
    'home': HomeSitemap,
}
