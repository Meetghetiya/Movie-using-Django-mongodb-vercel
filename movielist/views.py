import requests
from django.shortcuts import render,redirect
from django.contrib import messages
from .models import Movie

def index(request,page=1):
    api_key = '678701dc7dc66aa11759f9b9a836fcb9'  # Replace with your actual API key
    url = f'https://api.themoviedb.org/3/discover/movie?api_key={api_key}&sort_by=popularity.desc&with_genres=28&page={page}'
    
    response = requests.get(url)
    data = response.json()

    movies = data['results']
    total_pages = data['total_pages']

     # Clear accumulated movies from the session when accessing a new page
    if page == 1:
        request.session.pop('accumulated_movies', None)

    # Get the previously accumulated movies from the session, or an empty list if it doesn't exist yet
    accumulated_movies = request.session.get('accumulated_movies', [])

    # Append the new movies to the accumulated list
    accumulated_movies += movies

    # Update the accumulated movies in the session
    request.session['accumulated_movies'] = accumulated_movies

     # Retrieve genre data
    genres = get_genres()

    context = {
        'movies': accumulated_movies,
        'genres': genres,
        'page': page,
        'total_pages': total_pages,
    }
    return render(request,'index.html',context)


def get_genres():
    api_key = '678701dc7dc66aa11759f9b9a836fcb9'  # Replace with your actual API key
    genre_url = f'https://api.themoviedb.org/3/genre/movie/list?api_key={api_key}'
    genre_response = requests.get(genre_url)
    genre_data = genre_response.json()
    genres = genre_data['genres']
    return genres


def movie_detail(request, movie_id):
    api_key = '678701dc7dc66aa11759f9b9a836fcb9'  # Replace with your API key
    url = f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}'

    try:
        response = requests.get(url)
        movie_data = response.json()
        genres_datas = movie_data['genres']
        poster = movie_data['poster_path']
        title = movie_data['title']
        genres = [genres_data['name'] for genres_data in genres_datas ]
        release_date = movie_data['release_date']
        runtime = movie_data['runtime']
        overview = movie_data['overview']
        # Retrieve other movie details from the movie_data dictionary
    except requests.exceptions.RequestException as e:
        movie_name = "Movie not found"
        # Handle the case when the movie data cannot be fetched or an error occurs

    context = {
        'movie_id': movie_id,
        'movie_data': movie_data, 
        'genres': genres, 
        'poster': poster, 
        'title': title, 
        'overview': overview, 
        'release_date': release_date, 
        'runtime': runtime,
        'movie_id': movie_id,
    }

    return render(request, 'moviedetail.html', context)


def category_movies(request,id,page=1,category="category_movies"):
    api_key = '678701dc7dc66aa11759f9b9a836fcb9'
    url = f'https://api.themoviedb.org/3/discover/movie?api_key={api_key}&with_genres={id}&page={page}'
    
    response = requests.get(url)
    data = response.json()
    movies = data['results']
    total_pages = data['total_pages']


    if page == 1:
        request.session.pop('accumulated_movies', None)

    # Get the previously accumulated movies from the session, or an empty list if it doesn't exist yet
    accumulated_movies = request.session.get('accumulated_movies', [])

    # Append the new movies to the accumulated list
    accumulated_movies += movies

    # Update the accumulated movies in the session
    request.session['accumulated_movies'] = accumulated_movies

    context = {
        'movies': accumulated_movies,
        'page': page,
        'total_pages': total_pages,
        'id': id,
        'category': category,
        }
    return render(request, 'categorymovies.html', context)




def add_to_watchlist(request, movie_id):
    api_key = '678701dc7dc66aa11759f9b9a836fcb9'
    response = requests.get(f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}')
    movie_data = response.json()
    
    if request.user.is_authenticated:
        movie = Movie(
            user=request.user,
            movie_id = movie_data['id'],
            title=movie_data['title'],
            overview=movie_data['overview'],
            release_date=movie_data['release_date'],
            vote_average=movie_data['vote_average'],
            runtime=movie_data['runtime'],
            poster=movie_data['poster_path'],
            genres=movie_data['genres']
        )
        movie.save()
        return redirect('/movies/watchlist/')
    else:
        messages.info(request, "You must be logged in to add movies to your watchlist.")
        return redirect(request.META.get('HTTP_REFERER', 'index'))



def watchlist(request):

    if request.user.is_authenticated:
      movies = Movie.objects.filter(user=request.user)
      return render(request, 'watchlist.html', {'movies': movies})
    else:
      messages.info(request, "You must be logged in to shaw your watchlist.")
      return redirect(request.META.get('HTTP_REFERER', 'index'))

def search(request):
      return render(request,'search.html')

def delete_movie(request, movie_id):
    try:
        movie = Movie.objects.get(pk=movie_id)
        movie.delete()
    except Movie.DoesNotExist:
        pass

    return redirect('/movies/watchlist/')  



def get_movies_by_name(movie_name):
    api_key = '678701dc7dc66aa11759f9b9a836fcb9'
    url = f'https://api.themoviedb.org/3/search/movie?api_key={api_key}&query={movie_name}'

    response = requests.get(url)
    data = response.json()

    movies = []
    if 'results' in data:
        results = data['results']
        for movie_data in results:
            movie = {
                'title' :movie_data['title'],
                'id' :movie_data['id'],
                'overview': movie_data['overview'],
                'release_date': movie_data['release_date'],
                'vote_average': movie_data['vote_average'],
                'poster': movie_data['poster_path'],
            }
            movies.append(movie)

    return movies

def search_movie(request):
    if request.method == 'POST':
        movie_name = request.POST.get('movie_name')
        if movie_name:
            movies = get_movies_by_name(movie_name)
            return render(request, 'search.html', {'movies': movies})

    return render(request, 'search.html')
