from django.contrib import admin

from blog.models import News, Post, Category, Tag, Comment

admin.site.register(Post)
admin.site.register(Category)
admin.site.register(Tag)
admin.site.register(Comment)


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ['post_title', 'is_important', 'news_type', 'pinned', 'email_notifications_sent'] # Можно так: post_item__title
    list_filter = ['is_important', 'news_type', 'pinned', 'email_notifications_sent']
    
    def post_title(self, obj):
        return obj.post_item.title
    post_title.short_description = 'Заголовок'
