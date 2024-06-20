from rest_framework import serializers
from .models import Post, Like, Comment, CommentLike, User



class UserSerializers(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    
    class Meta:
        model = User
        fields = ('id', 'username', 'photo')
        
class PostSerializers(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    author = UserSerializers(read_only=True)
    post_likes_count = serializers.SerializerMethodField('get_post_likes')
    post_comment_count = serializers.SerializerMethodField('get_post_comment')
    me_like = serializers.SerializerMethodField('get_me_liked')
    
    class Meta:
        model = Post
        fields = (
            "id",
            "author",
            "image",
            'post',
            "created_time",
            "post_likes_count",
            "post_comment_count",
            "me_like"
        )
        extra_kwargs = {"image":{"required":False}}
        
    def get_post_likes(self, obj):
        return obj.likes.count()
    def get_post_comment(self, obj):
        return obj.comment.count()
    def get_me_liked(self, obj):
        request = self.context.get("request")
        
        if request and request.user.is_authenticated:
            try:
                like = Like.objects.get(post=obj, user=request.user)
                return True
            except Post.DoesNotExist:
                return False
            
            
class CommentSerializers(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    user = UserSerializers(read_only=True)
    replies = serializers.SerializerMethodField('get_replies')
    me_like = serializers.SerializerMethodField('get_me_liked')
    likes_count = serializers.SerializerMethodField('get_likes_count')
    
    
    class Meta:
        model = Comment
        fields = (
            'id',
            'user',
            'comment',
            'post',
            'created_time',
            'me_like',
            'likes_count',
            'replies'
        )
    def get_replies(self, obj):
        if obj.commentComment.exists():
            serializers =  self.__class__(obj.commentComment.all(), many=True, context=self.context)
            
            return serializers.data
        else:
            return None
        
    try:
        def get_me_liked(self, obj):

            user = self.context.get('request').user
            
            if user.is_authenticated:
                return obj.commentlike.filter(user=user).exists()
            else:
                return False
    except:
        print('Xatolik!')
        
    def get_likes_count(self, obj):
        print(obj)
        return obj.commentlike.count()
    
    
class CommentLikeSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    
    user = UserSerializers(read_only=True)
    
    class Meta:
        model =CommentLike
        fileds = (
            'id',
            'user',
            'comment'
        )
        
        
class LikeSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    user = UserSerializers(read_only=True)
    class Meta:
        
        model =Like
        fileds = (
            'id',
            'user',
            'post'
        )