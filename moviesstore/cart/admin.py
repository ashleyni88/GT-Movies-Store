from django.contrib import admin
from .models import Order, Item, User
from django.db.models import Sum
from django.template import Context
from django.template.response import TemplateResponse
from django.urls import path

# Register your models here.

class PurchaseUserAdmin(admin.ModelAdmin):

    def get_urls(self):
        custom_urls = [path("top_purchasers/", self.admin_site.admin_view(self.top_purchasers), name="cart_order_top_purchasers")]
        return custom_urls + super().get_urls() 

    def top_purchasers(self, request):
        purchasers = (
            User.objects.annotate(movies_purchased= Sum("order__item__quantity", default=0))
        ).filter(movies_purchased__gt=0).order_by("-movies_purchased", "username", "pk")


        top_user = purchasers.first()

        if top_user is None:
            leaders = [] ##safety check
        else:
            leaders = purchasers.filter(movies_purchased= top_user.movies_purchased)

        # context = (
        #     self.admin_site.each_context(request),
        #     "title": "Top Movie Purchasers",
        #     "leaders": leaders,
        # )
        context = {**self.admin_site.each_context(request), "title": "Top Movie Purchasers", "leaders": leaders,}

        return TemplateResponse(request, "admin/cart/top_purchasers.html", context)

admin.site.register(Order, PurchaseUserAdmin)
admin.site.register(Item)

