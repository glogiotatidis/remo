import datetime
from random import randint

from django.db.models.signals import pre_save, post_save
from django.contrib.auth.models import User, Group
from django.utils.timezone import utc

import factory
from factory import fuzzy
from product_details import product_details

from remo.profiles.models import (UserProfile, FunctionalArea,
                                  email_mentor_notification, create_profile,
                                  user_set_inactive_post_save)


COUNTRIES = product_details.get_regions('en').values()
START_DT = datetime.datetime(2011, 1, 1, tzinfo=utc)


class OutOfRangeError(Exception):
    pass


def int2roman(n):
    roman_map = (('M', 1000), ('CM', 900), ('D', 500), ('CD', 400),
                 ('C', 100), ('XC', 90), ('L', 50), ('XL', 40), ('X', 10),
                 ('IX', 9), ('V', 5), ('IV', 4), ('I', 1))

    if not (0 < n < 5000):
        raise OutOfRangeError
    result = ''
    for numeral, integer in roman_map:
        while n >= integer:
            result += numeral
            n -= integer
    return result


class UserProfileFactory(factory.django.DjangoModelFactory):
    """UserProfile fixture factory."""
    FACTORY_FOR = UserProfile

    registration_complete = True
    date_joined_program = fuzzy.FuzzyDateTime(START_DT)
    local_name = 'Local Name'
    birth_date = datetime.date(1992, 1, 1)
    city = 'User city'
    region = 'User region'
    country = fuzzy.FuzzyChoice(COUNTRIES)
    lat = fuzzy.FuzzyInteger(-90, 90)
    lon = fuzzy.FuzzyInteger(-180, 180)
    display_name = factory.Sequence(lambda n: 'UserProfile%s' % n)
    private_email = factory.Sequence(lambda n: 'personal%s@example.com' % n)
    mozillians_profile_url = 'https://mozillians.org/'
    irc_name = factory.Sequence(lambda n: 'user%s' % n)
    wiki_profile_url = 'https://wiki.mozilla.org/User:'
    gender = fuzzy.FuzzyChoice([None, True, False])

    @classmethod
    def _create(cls, target_class, *args, **kwargs):
        dispatch_uid = 'userprofile_email_mentor_notification'
        pre_save.disconnect(email_mentor_notification, UserProfile,
                            dispatch_uid=dispatch_uid)
        profile = super(UserProfileFactory, cls)._create(target_class,
                                                         *args, **kwargs)
        pre_save.connect(email_mentor_notification, UserProfile,
                         dispatch_uid=dispatch_uid)
        return profile

    @factory.post_generation
    def functional_areas(self, create, extracted, **kwargs):
        """Add functional areas list after object generation."""
        if not create:
            return
        if extracted:
            for area in extracted:
                self.functional_areas.add(area)

    @factory.post_generation
    def random_functional_areas(self, create, extracted, **kwargs):
        """Add random functional areas after object generation."""
        if not create:
            return
        if extracted:
            rand_int = randint(1, FunctionalArea.objects.count())
            for area in FunctionalArea.objects.all().order_by('?')[:rand_int]:
                self.functional_areas.add(area)

    @factory.post_generation
    def initial_council(self, create, extracted, **kwargs):
        """Create userprofile with self as mentor."""
        if not create:
            return
        if extracted:
            self.mentor = self.user


class UserFactory(factory.django.DjangoModelFactory):
    """User model factory."""
    FACTORY_FOR = User

    username = factory.Sequence(lambda n: 'username%s' % n)
    first_name = 'John'
    last_name = factory.Sequence(lambda n: 'Doe %s' % int2roman(n))
    email = factory.LazyAttribute(lambda o: '%s@example.com' % o.username)
    password = factory.PostGenerationMethodCall('set_password', 'passwd')
    is_staff = False
    is_active = True
    is_superuser = False
    last_login = datetime.datetime(2012, 1, 1)
    date_joined = datetime.datetime(2011, 1, 1)
    userprofile = factory.RelatedFactory(UserProfileFactory, 'user')

    @classmethod
    def _create(cls, target_class, *args, **kwargs):
        post_save.disconnect(create_profile, User,
                             dispatch_uid='create_profile_signal')
        post_save.disconnect(user_set_inactive_post_save, User,
                             dispatch_uid='user_set_inactive_post_save_signal')
        user = super(UserFactory, cls)._create(target_class, *args, **kwargs)
        post_save.connect(create_profile, User,
                          dispatch_uid='create_profile_signal')
        post_save.connect(user_set_inactive_post_save, User,
                          dispatch_uid='user_set_inactive_post_save_signal')
        return user

    @factory.post_generation
    def groups(self, create, extracted, **kwargs):
        """Add list of groups to User object."""
        if not create:
            return
        if extracted:
            groups = Group.objects.filter(name__in=extracted)
            self.groups.add(*groups)


class FunctionalAreaFactory(factory.django.DjangoModelFactory):
    """FunctionalArea fixture factory."""
    FACTORY_FOR = FunctionalArea

    name = factory.Sequence(lambda n: 'Functional Area #%s' % n)
