from django.shortcuts import render
from rest_framework import generics
from .serializers import PostSerializers, CommentSerializers, LikeSerializer, CommentLikeSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
from .models import Post, Comment, Like, CommentLike
from shared.pagination import CustomPagination
from rest_framework.response import Response 
from rest_framework import status
from rest_framework.views import APIView

class PostListView(generics.ListAPIView): ### postni(yaniy-rasm,video) kurish uchun views
    serializer_class = PostSerializers
    permission_classes = [AllowAny, ]
    pagination_class = CustomPagination
    
    def get_queryset(self):
        return Post.objects.all()
    
    
class PostCreate(generics.CreateAPIView): ### rasm video joylash uchun views
    serializer_class = PostSerializers
    permission_classes = [IsAuthenticated, ]
    
    def perfrom_create(self, serializer):
        serializer.save(user=self.request.user)
        
        
class PostUpdateRetriveDelete(generics.RetrieveUpdateDestroyAPIView):  ### POSTNI(POST BU VIDEO YOKI RASM) KURISH, UCHIRISH VA UZGARTIRISH(REDAKTIROVAT)
    serializer_class = PostSerializers
    permission_classes = [IsAuthenticatedOrReadOnly, ]
    
    def put(self, request, *args, **kwargs):
        serializer = self.serializer_class
        post = self.get_object()
        serializer = serializer(post, data=request.data)
        serializer.is_valid(raise_exception=True)
        
        serializer.save()
        
        return Response({'message':"Update"}, status=status.HTTP_200_OK)
    
    def delete(self, request, *args, **kwargs):
        post = self.get_object()
        
        post.delete()
        return Response({'message':"Delete"}, status=status.HTTP_200_OK)
    
    
class PostCommentListView(generics.ListAPIView):
    serializer_class = CommentSerializers
    permission_classes = [AllowAny, ]
    def get_queryset(self):
        post_id = self.kwargs['pk']
        queryset = Comment.objects.filter(post_id=post_id)
        return queryset 
    
    
    
class PostCommentCreateView(generics.CreateAPIView): ### COMENT YOZISH
    serializer_class = CommentSerializers
    permission_classes = [IsAuthenticated, ]
    
    def perfrom_create(self, serializer):
        post_id = self.kwargs['pk']
        serializer.save(author=self.request.user, post_id=post_id)
        
    

class CommentListCreateApiView(generics.ListCreateAPIView): ### COMENT YOZISH VA KURISH
    serializer_class = CommentSerializers
    permission_classes = [IsAuthenticatedOrReadOnly, ]
    
    def perfrom_create(self, serializer):
        serializer.save(author=self.request.user)
        
    queryset = Comment.objects.all()
        
        
class CommentRetrieveView(generics.RetrieveAPIView): ### COMENTNI KURISH
    serializer_class = CommentSerializers
    permission_classes = [AllowAny, ]
    queryset = Comment.objects.all()
    
class PostLikeListView(generics.ListAPIView): ### POSTNI LIKELARINI KURISH UCHUN
    serializer_class = LikeSerializer
    permission_classes = [AllowAny, ]
    
    def get_queryset(self):
        post_id = self.kwargs['pk']
        return Like.objects.filter(post_id=post_id)
    
    
class CommentLikeListView(generics.ListAPIView): ### COMMENTLARNI LIKENI KURISH
    serializer_class = CommentLikeSerializer
    permission_classes = [AllowAny, ]
    
    def get_queryset(self):
        comment_id = self.kwargs['pk']
        return CommentLike.objects.filter(comment_id=comment_id) 
    
    
    
class PostLikeApiview(APIView):  ### BU AGAR LIKE BOSGAN BUSEN USTIGA YANA BOSSEN LIKENI UCHIRADI AGAR YUQ BUSA LIKE BOSILADI
    
    def post(self, request, pk):
        try:
            post_like = Like.objects.get(
                author=self.request.user,
                post_id=pk,
            )
            post_like.delete()
            data = {
                'success': True,
                'message': "LIKE muvvafaqiyatli o'chirildi"
            }
            return Response(data, status=status.HTTP_204_NO_CONTENT)
        except Like.DoesNotExist:
            post_like = Like.objects.create(
                author=self.request.user,
                post_id=pk
            )
            serializer = LikeSerializer(post_like)
            data = {
                'success':True,
                'message': "Post LIKE muvoffaqiyatli qo'shildi",
                'data':serializer.data
            }
            return Response(data, status=status.HTTP_201_CREATED)
    
    
class CommentLikeApiView(APIView): ### BU AGAR COMMENT LIKE BOSGAN BUSEN USTIGA YANA BOSSEN COMMENDE LIKENI UCHIRADI AGAR YUQ BUSA LIKE BOSILADI
    def post(self,request,pk):
        try:
            
            comment_like = CommentLike.objects.get(
                user=self.request.user,
                comment_id=pk
            )
            comment_like.delete()
            data = {
                'success':True,
                'message': "Comment LIKE muvoffaqiyatli o'chirildi",
                'data':None
            }
            return Response(data, status=status.HTTP_204_NO_CONTENT)
        except CommentLike.DoesNotExist:
            comment_like = CommentLike.objects.create(
                user=self.request.user,
                comment_id=pk
            )
            serializer = CommentLikeSerializer(comment_like)
            data = {
                'success':True,
                'message': "LIKE muvoffaqiyatli qo'shildi",
                'data':serializer.data
            }
            return Response(data, status=status.HTTP_201_CREATED)