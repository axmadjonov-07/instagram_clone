from django.db import models
from shared.models import BaseModel
from django.core.validators import FileExtensionValidator
from user.models import User

class Post(BaseModel):
    user = models.ForeignKey("user.User", related_name="posts", on_delete=models.CASCADE)
    image = models.ImageField(upload_to="images/post_images", validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])])
    post = models.CharField(max_length=250)
    
    class Meta:
        db_table = 'post'
        
    def __str__(self):
        return self.post
    
    
class Like(BaseModel):
    user = models.ForeignKey("user.User", related_name="like", on_delete=models.CASCADE)
    post = models.ForeignKey("post.Post", related_name="likes", on_delete=models.CASCADE)
    
    class Meta:
        db_table = "like"
    
class Comment(BaseModel):
    user = models.ForeignKey("user.User", related_name="comments", on_delete=models.CASCADE)
    comment = models.CharField(max_length=250)
    post = models.ForeignKey("post.Post", related_name="comment", on_delete=models.CASCADE)
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null = True,
        blank = True,
        related_name = "commentComment"
        )
        
    class Meta:
        db_table = 'comment'
        
    def __str__(self):
        return self.comment
    
        
class CommentLike(BaseModel):
    user = models.ForeignKey("user.User", related_name="commentlikes", on_delete=models.CASCADE)
    comment = models.ForeignKey("post.Comment", related_name="commentlike", on_delete=models.CASCADE)
    
    class Meta:
        db_table = "comment_like"
    
