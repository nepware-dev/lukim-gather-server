from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers

from .models import Comment, LikeComment


class CommentSerializer(serializers.ModelSerializer):
    content_type = serializers.SlugRelatedField(
        queryset=ContentType.objects.all(),
        slug_field="model",
    )
    total_likes = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = "__all__"

    def get_total_likes(self, obj):
        return obj.likes.count()


class LikeCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = LikeComment
        fields = "__all__"
        read_only_fields = ("user",)
