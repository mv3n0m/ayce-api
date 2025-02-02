from src.docs import get_docs
from .helpers import handle_jwt
from src.utils import responsify


def use_auth(_auth="jwt", _identity="False"):
    def decorator(func):
        def _wrapper(_auth=_auth, _identity=_identity, *args, **kwargs):
            if _auth and _auth.endswith("jwt"):
                response = handle_jwt(_identity)
                if "error" in response[0]:
                    return responsify(*response)

                _kwargs, _user = response
                args = (_user, *args)
                kwargs.update(_kwargs)

            return func(*args, **kwargs)

        _wrapper.__name__ = func.__name__
        return _wrapper
    return decorator


def route_wrapper(bp, use_kwargs, url_prefix, route, methods=["GET"], _args={}, _auth="jwt", _identity=False, *args, **kwargs):
    def decorator(func):
        @bp.route(route, methods=methods)
        @use_auth(_auth, _identity)
        @use_kwargs(_args)
        def _wrapper(*inner_args, **inner_kwargs):
            return func(*inner_args, **inner_kwargs)

        _wrapper.__doc__ = get_docs(route, url_prefix, methods[0], _args, _auth)
        # print(_wrapper.__doc__)
        _wrapper.__name__ = func.__name__
        return _wrapper
    return decorator

