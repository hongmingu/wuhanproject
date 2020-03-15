from django.contrib import admin
from .models import BlogPost, Comment, PostView, Category
# Register your models here.

admin.site.register(BlogPost)
admin.site.register(Comment)
admin.site.register(PostView)
admin.site.register(Category)