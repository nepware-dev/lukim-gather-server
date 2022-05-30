from graphql_jwt.exceptions import PermissionDenied


def staff_resolver(attname, default_value, root, info, **args):
    if info.context.user.is_staff:
        return getattr(root, attname, default_value)
    raise PermissionDenied()
