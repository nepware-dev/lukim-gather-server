import logging
from functools import wraps

from django.utils.translation import gettext_lazy as _
from ratelimit import ALL
from ratelimit.exceptions import Ratelimited
from ratelimit.utils import is_ratelimited

logger = logging.getLogger(__name__)


def GQLRateLimitKey(group, request):
    return request.gql_rl_field


def ratelimit(group=None, key=None, rate=None, method=ALL, block=False):
    def decorator(fn):
        @wraps(fn)
        def _wrapped(root, info, **kwargs):
            request = info.context

            old_limited = getattr(request, "limited", False)

            if key and key.startswith("gql:"):
                _key = key.split("gql:")[1]
                if "." in _key:
                    _key = _key.split(".")
                    value = kwargs.get(_key[-2], {}).get(_key[-1], None)
                else:
                    value = kwargs.get(_key, None)
                if not value:
                    raise ValueError(f"Cannot get key: {key}")
                request.gql_rl_field = value

                new_key = GQLRateLimitKey
            else:
                new_key = key

            ratelimited = is_ratelimited(
                request=request,
                group=group,
                fn=fn,
                key=new_key,
                rate=rate,
                method=method,
                increment=True,
            )

            request.limited = ratelimited or old_limited

            if ratelimited and block:
                raise Ratelimited("rate_limited")
            return fn(root, info, **kwargs)

        return _wrapped

    return decorator
