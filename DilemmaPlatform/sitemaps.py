from django.contrib.sitemaps import Sitemap
from django.urls import reverse


class StaticSitemap(Sitemap):
    """Reverse 'static' views for XML sitemap."""
    changefreq = "weekly"
    protocol = 'https'
    static_url_list = [
        {'url': 'home', 'priority': 0.8, 'changefreq': "monthly"},
        {'url': 'contact_us', 'priority': 0.6, 'changefreq': "weekly"},
        {'url': 'blog', 'priority': 0.4, 'changefreq': "weekly"}
    ]

    def items(self):
        # Return list of url names for views to include in sitemap
        return ['users:about', 'users:login', 'users:register',
                'users:dashboard', 'users:settings', 'users:help',
                'users:contact', 'users:universities', 'users:about_us',
                'users:privacy', 'payments:pricing', 'payments:subterms']

    def location(self, item):
        return reverse(item)

    def priority(self, item):
        return {
            'users:about': 1.0,
            'users:contact': 1.0,
            'users:login': 1.0,
            'users:register': 1.0,
            'users:help': 0.7,
            'users:universities': 0.7,
            'users:about_us': 0.7,
            'users:privacy': 0.7,
            'payments:pricing': 0.7,
            'payments:subterms': 0.7,
            'users:dashboard': 0.5,
            'users:settings': 0.5,
        }[item]
