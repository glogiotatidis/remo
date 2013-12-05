from functools import wraps

from django.contrib import messages
from django.shortcuts import redirect

from remo.base.utils import get_object_or_none


def permission_check(permissions=[], group=None,
                     filter_field=None, owner_field=None, model=None):
    """Check if a user is logged in and has the required permissions.

    1. If user is not logged in then redirect to 'main', display login
    message

    2. If user logged in and len(/permissions/) == 0, group != None
    and /filter_field/ == None then allow access

    3. If user logged in and len(/permissions/) > 0, group != None
    and /filter_field/ == None then allow access only if user has all
    permissions

    4. If user logged in and len(/permissions/) > 0 and group == None
    and /filter_field/ != None then allow access if user has all
    permissions or there is an object in /model/ with attributes
    /filter_field/ == kwargs[filter_field] and /owner_field/ ==
    request.user.

    5. If user logged in and len(permissions) == 0 and group == None
    and filter_field != None then allow access only if there is an
    object in /model/ with attributes /filter_field/ ==
    kwargs[filter_field] and /owner_field/ == request.user.

    6. If user logged in and len(permissions) == 0 and group != None
    and /filter_field/ == None then allow access if user is member of Group.

    7. If user logged in and len(/permissions/) > 0 and group != None
    and /filter_field/ != None then allow access if user has all
    permissions or is part of group or there is an object in /model/
    with attributes /filter_field/ == kwargs[filter_field] and
    /owner_field/ == request.user.

    8. If user logged in and len(permissions) == 0 and group != None
    and filter_field != None then allow access only if user is part of
    group or there is an object in /model/ with attributes
    /filter_field/ == kwargs[filter_field] and /owner_field/ ==
    request.user.

    """

    def decorator(func):

        @wraps(func)
        def wrapper(request, *args, **kwargs):

            def _check_if_user_has_permissions():
                if (((permissions and request.user.has_perms(permissions)) or
                     request.user.groups.filter(name=group).exists())):
                    return True
                return False

            def _check_if_user_owns_page():
                if owner_field and model:
                    if not kwargs.get(filter_field):
                        return True

                    obj = get_object_or_none(model, **{filter_field:
                                                       kwargs[filter_field]})
                    if obj and getattr(obj, owner_field) == request.user:
                        return True
                return False

            if request.user.is_authenticated():
                if (((not permissions and not group and not filter_field) or
                     request.user.is_superuser or
                     _check_if_user_owns_page() or
                     _check_if_user_has_permissions())):
                    return func(request, *args, **kwargs)
                else:
                    messages.error(request, 'Permission denied.')
                    return redirect('main')
            else:
                messages.warning(request, 'Please login.')
                request.session['next_url'] = request.get_full_path()
                return redirect('main')

        return wrapper
    return decorator
