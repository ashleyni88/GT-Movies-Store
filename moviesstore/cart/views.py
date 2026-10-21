from django.shortcuts import render
from django.shortcuts import get_object_or_404, redirect
from movies.models import Movie
from .utils import calculate_cart_total
from .models import Order, Item
from django.contrib.auth.decorators import login_required
from .regions import REGION_CHOICES
from django.db import transaction
from django.urls import reverse
from django.views.decorators.http import require_POST


# Create your views here.
def index(request):
    cart_total = 0
    movies_in_cart = []
    cart = request.session.get('cart', {})
    movie_ids = list(cart.keys())
    if (movie_ids != []):
        movies_in_cart = Movie.objects.filter(id__in=movie_ids)
        cart_total = calculate_cart_total(cart,
            movies_in_cart)
    template_data = {}
    template_data['title'] = 'Cart'
    template_data['movies_in_cart'] = movies_in_cart
    template_data['cart_total'] = cart_total
    template_data["region_choices"] = REGION_CHOICES
    if request.GET.get("region_error"):
        template_data["region_error"] = (
            "Please select a valid region before purchasing."
        )
    return render(request, 'cart/index.html',
        {'template_data': template_data})

def add(request, id):
    get_object_or_404(Movie, id=id)
    cart = request.session.get('cart', {})
    cart[id] = request.POST['quantity']
    request.session['cart'] = cart
    return redirect('cart.index')

def clear(request):
    request.session['cart'] = {}
    return redirect('cart.index')

@login_required(login_url = "accounts.login")
@require_POST
def purchase(request):
    region = request.POST.get("region", "")
    if region not in dict(REGION_CHOICES):
        return redirect(
            reverse("cart.index") + "?region_error=1"
        )
    
    cart = request.session.get('cart', {})
    if not cart:
        return redirect("cart.index")
    movies_in_cart = list(
        Movie.objects.filter(id__in=cart.keys())
    )
    if len(movies_in_cart) != len(cart):
        return redirect("cart.index")
    try:
        quantities = {
            movie.id: int(cart[str(movie.id)])
            for movie in movies_in_cart
        }
    except(ValueError, TypeError, KeyError):
        return redirect("cart.index")

    if any(
        quantity < 1
        for quantity in quantities.values()
    ):
        return redirect("cart.index")
    cart_total = sum(
        movie.price * quantities[movie.id]
        for movie in movies_in_cart
    )
    with transaction.atomic():
        order = Order.objects.create(
            user = request.user,
            total = cart_total,
            region = region,
        )
        for movie in movies_in_cart:
            Item.objects.create(
                movie=movie,
                price= movie.price,
                order=order,
                quantity=quantities[movie.id],
            )

    request.session["cart"] = {}
    template_data = {
        "title": "Purchase confirmation",
        "order_id": order.id,
    }

    return render(
        request,
        "cart/purchase.html",
        {"template_data": template_data},
    )
