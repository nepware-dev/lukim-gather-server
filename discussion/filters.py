from django_filters import FilterSet

from discussion.models import Comment, LikeComment


class CommentFilter(FilterSet):
    class Meta:
        model = Comment
        fields = {
            "id": ["exact"],
            "user": ["exact"],
            "content_type": ["exact"],
            "content_type__app_label": ["exact"],
            "content_type__model": ["exact"],
            "object_id": ["exact"],
            "parent": ["exact"],
            "level": ["exact"],
            "created_at": ["gte", "lte"],
            "modified_at": ["gte", "lte"],
        }

    @property
    def qs(self):
        return super().qs.order_by("-created_at")


class LikeCommentFilter(FilterSet):
    class Meta:
        model = LikeComment
        fields = {
            "comment": ["exact"],
            "created_at": ["gte", "lte"],
            "modified_at": ["gte", "lte"],
        }
