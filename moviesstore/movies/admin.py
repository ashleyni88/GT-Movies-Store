from django.contrib import admin
from django.db.models import Count, Sum
from django.contrib.admin import models
from .models import Movie, Review
from django.urls import path
from django.template.response import TemplateResponse

from django.contrib.auth.models import User
# Register your models here.
class MovieAdmin(admin.ModelAdmin):
    ordering = ['name']

    def get_urls(self):
        custom_urls = [
            path(
                "engagement/",
                self.admin_site.admin_view(
                    self.engagement_report
                ),
                name = "movies_movie_engagement",
            ),
        ]
        return custom_urls + super().get_urls()

    def engagement_report(self, request):
        # Defining the movie with the highest purchase count
        most_purchased = (
            Movie.objects.annotate (
                purchase_count = Sum(
                    "item__quantity", default = 0
                    )
                )
                .filter(purchase_count__gt = 0)
                .order_by("-purchase_count", "name", "pk")
                .first()
            )

        # Finding the movie that has the highets written reviews
        most_reviewed = (
            Movie.objects.annotate(
                review_count = Count("review")
            )
            .filter(review_count__gt = 0)
            .order_by("-review_count", "name", "pk")
            .first()
        )

        context = {
            **self.admin_site.each_context(request),
            "title" : "Movie Analytics",
            "most_purchased" : most_purchased,
            "most_reviewed" : most_reviewed,
        }

        return TemplateResponse(
            request,
            "admin/movies/movie_engagement.html",
            context
        )
        


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
