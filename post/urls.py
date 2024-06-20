from django.urls import path
from . import views

urlpatterns = [
    path("posts/", views.PostListView.as_view()),
    path("create/", views.PostCreate.as_view()),
    path("post/<uuid:pk>", views.PostUpdateRetriveDelete.as_view()),
    path("<uuid:pk>/comments/", views.PostCommentListView.as_view()),
    path("<uuid:pk>/likes/", views.PostLikeListView.as_view()),
    path("<uuid:pk>/comments/create/", views.PostCommentCreateView.as_view()),
    path("comments/", views.CommentListCreateApiView.as_view()),
    path("comments/<uuid:pk>/", views.CommentRetrieveView.as_view()),
    path("comments/<uuid:pk>/likes/", views.CommentLikeListView.as_view()),
    path("<uuid:pk>/create-delete-like/", views.PostLikeApiview.as_view()),
    path("comments/<uuid:pk>/create-delete-like/", views.CommentLikeApiView.as_view())
    
]
