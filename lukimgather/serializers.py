from django.contrib.auth import get_user_model
from rest_framework.serializers import ModelSerializer

UserModel = get_user_model()


class UserModelSerializer(ModelSerializer):
    def build_relational_field(self, field_name, relation_info):
        if (
            relation_info.related_model == get_user_model()
            and relation_info.to_field is None
        ):
            relation_info = relation_info._replace(to_field="username")
        return super().build_relational_field(field_name, relation_info)
