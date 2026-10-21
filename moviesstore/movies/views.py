from django.shortcuts import render, redirect, get_object_or_404
from .models import Movie, Review, Rating
from django.contrib.auth.decorators import login_required
from django.db.models import Avg
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from cart.models import Item
from cart.regions import REGIONS
# Create your views here.

def index(request):
    search_term = request.GET.get('search')
    if search_term:
        movies = Movie.objects.filter(name__icontains=search_term)
    else:
        movies = Movie.objects.all()
    template_data = {}
    template_data['title'] = 'Movies'
    template_data['movies'] = movies
    return render(request, 'movies/index.html', {'template_data': template_data})
def show(request, id):
    movie = Movie.objects.get(id=id)
    # only shows the movies that aren't flagged as 'is_inappropriate'
    reviews = Review.objects.filter(movie=movie, is_inappropriate=False)
    template_data = {}
    template_data['title'] = movie.name
    template_data['movie'] = movie
    template_data['reviews'] = reviews
    template_data['average_rating'] = Rating.objects.filter(movie=movie).aggregate(Avg('rating'))['rating__avg']
    if request.user.is_authenticated:
        template_data['user_rating'] = Rating.objects.filter(movie=movie, user=request.user).first()
    return render(request, 'movies/show.html', {'template_data': template_data})
@login_required
def create_review(request, id):
    if request.method == 'POST' and request.POST['comment'] != '':
        movie = Movie.objects.get(id=id)
        review = Review()
        review.comment = request.POST['comment']
        review.movie = movie
        review.user = request.user
        review.save()
        return redirect('movies.show', id=id)
    else:
        return redirect('movies.show', id=id)

@login_required
def edit_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id)
    if request.user != review.user:
        return redirect('movies.show', id=id)
    if request.method == 'GET':
        template_data = {}
        template_data['title'] = 'Edit Review'
        template_data['review'] = review
        return render(request, 'movies/edit_review.html',
            {'template_data': template_data})
    elif request.method == 'POST' and request.POST['comment'] != '':
        review = Review.objects.get(id=review_id)
        review.comment = request.POST['comment']
        review.save()
        return redirect('movies.show', id=id)
    else:
        return redirect('movies.show', id=id)

@login_required
def delete_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)
    review.delete()
    return redirect('movies.show', id=id)

# flags innapropriate comments and gets reported reasoning
@login_required
def report_review(request, id, review_id):
    if request.method == 'POST':
        review = get_object_or_404(Review, id=review_id, movie_id=id)
        review.is_inappropriate = True
        reason = request.POST.get('reason')
        if reason:
            review.report_reason = reason
        review.save()
    return redirect('movies.show', id=id)

@login_required
def rate_movie(request, id):
    if request.method == 'POST':
        movie = get_object_or_404(Movie, id=id)
        Rating.objects.update_or_create(movie=movie, user=request.user,
                                        defaults={'rating': int(request.POST['rating'])})
    return redirect('movies.show', id=id)

@login_required(login_url="accounts.login")
def local_popularity(request):
    region_codes = {
        region["code"]
        for region in REGIONS
    }
    selected_code = request.GET.get(
        "region",
        "southeast",
    )
    if selected_code not in region_codes:
        selected_code = "southeast"

    selected_region = next(
        region 
        for region in REGIONS
        if region["code"] == selected_code
    )

    rankings = list(
        Item.objects
        .filter(
            order__region__in=region_codes,
            quantity__gt = 0
        )
        .values(
            "order__region",
            "movie_id",
            "movie__name",
        )
        .annotate(purchases=Sum("quantity"))
        .order_by(
            "order__region",
            "-purchases",
            "movie__name",
            "movie_id",
        )
    )

    movies_by_region = {
        code: []
        for code in region_codes
    }

    for row in rankings:
        region_code = row["order__region"]
        movies_by_region[region_code].append(row)

    markers = []
    for region in REGIONS:
        regional_movies = movies_by_region[region["code"]]
        markers.append({
            **region,
            "total": sum(
                movie["purchases"]
                for movie in regional_movies
            ),
            "top_movie": (
                regional_movies[0]["movie__name"]
                if regional_movies
                else ""
            ),
        })
    own_purchases = (
        Item.objects
        .filter(
            order__user=request.user,
            order__region=selected_code,
            quantity__gt=0,
        )
        .values("movie_id", "movie__name")
        .annotate(purchases=Sum("quantity"))
        .order_by(
            "-purchases",
            "movie__name",
            "movie_id",
        )
    )

    return render(
        request,
        "movies/local_popularity.html",
        {
            "template_data": {
                "title": "Local Popularity Map",
            },
            "regions": REGIONS,
            "selected_region": selected_region,
            "top_movies": (
                movies_by_region[selected_code][:10]
            ),
            "own_purchases": own_purchases,
            "markers": markers,
        },
    )

