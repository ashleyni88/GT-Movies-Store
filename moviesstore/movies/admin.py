from django.contrib import admin
from django.db.models import Count
from django.contrib.admin import models
from .models import Movie, Review

from django.contrib.auth.models import User
# Register your models here.
class MovieAdmin(admin.ModelAdmin):
    ordering = ['name']
# Gives filtering for reviews so admin can see the innapropriate deleted comments
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['id', 'movie', 'user', 'comment', 'is_inappropriate', 'report_reason']
    list_filter = ['is_inappropriate']

class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'review_count']
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(review_count=Count('review'))

    def review_count(self, obj):
        return obj.review_count

    review_count.admin_order_field = 'review_count'
    
    


admin.site.register(Movie, MovieAdmin)
admin.site.register(Review, ReviewAdmin)
admin.site.unregister(User)  # Unregister the default User admin 
# blocks an error i think... we shall see
admin.site.register(User, UserAdmin)
