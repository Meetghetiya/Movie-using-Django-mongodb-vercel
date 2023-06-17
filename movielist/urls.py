from django.contrib import admin
from django.urls import path
from movielist import views

urlpatterns = [
   path('',views.index),
   path('movies/watchlist/<int:movie_id>/',views.add_to_watchlist,name='add_to_watchlist'),
   path('movies/watchlist/',views.watchlist,name='watchlist'),
   path('movies/delete/<int:movie_id>/',views.delete_movie,name='delete_movie'),
   path('movies/search/',views.search_movie,name='search_movie'),
   path('movies/page/<int:page>/', views.index, name='index'),
   path('movies/<int:movie_id>/',views.movie_detail,name='movie_detail'),
   path('movies/<str:category>/<int:id>/',views.category_movies,name='category_movies'),
   # path('movies/page/<int:page>/<int:id>/',views.category_movies,name='category_movies'),
   path('movies/<str:category>/<int:id>/<int:page>/',views.category_movies,name='category_movies')
]