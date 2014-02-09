from jingo import register


@register.filter
def get_users_voted(poll):
    """Return the number of users voted to the specific poll."""

    return poll.users_voted.all().count()

from django.contrib.auth.models import User

@register.filter
def get_voters_per_group(poll):
    """Return the number of users of a specific poll per group."""

    return User.objects.filter(groups=poll.valid_groups).count() 
