import pytz
from datetime import datetime

from django.db.models import F
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from remo.base.decorators import permission_check
from remo.voting.models import Poll, RadioPollChoice, RangePollChoice, Vote

import forms


@permission_check()
def list_votings(request):
    """List votings view."""
    user = request.user
    now = datetime.now()
    polls = Poll.objects.all()
    if not user.groups.filter(name='Admin').exists():
        polls = Poll.objects.filter(valid_groups__in=user.groups.all())

    past_polls = polls.filter(end__lt=now)
    current_polls = polls.filter(start__lt=now, end__gt=now)
    future_polls = polls.filter(start__gt=now)

    return render(request, 'list_votings.html',
                  {'user': user,
                   'past_polls': past_polls,
                   'current_polls': current_polls,
                   'future_polls': future_polls})


@permission_check(group='Admin')
def edit_voting(request, slug=None):
    """Create/Edit voting view."""
    return render(request, 'edit_voting.html')


@permission_check()
def view_voting(request, slug):
    """View voting and vote view."""
    user = request.user
    now = timezone.make_aware(datetime.now(), pytz.UTC)
    poll = get_object_or_404(Poll, slug=slug)
    range_poll = poll.rangepoll_set.all()
    radio_poll = poll.radiopoll_set.all()
    range_poll_choice = {}
    radio_poll_choice = {}
    for item in range_poll:
        range_poll_choice[item] = (RangePollChoice.objects
                                   .filter(range_poll=item))
    for item in radio_poll:
        radio_poll_choice[item] = (RadioPollChoice.objects
                                   .filter(radio_poll=item))

    data = {'user': user,
            'poll': poll,
            'range_poll_choice': range_poll_choice,
            'radio_poll_choice': radio_poll_choice}

    # if voting period has ended, display the results
    if now > poll.end:
        return render(request, 'view_voting.html', data)
    if now < poll.start:
        messages.warning(request, ('This vote has not yet begun. '
                                   'You can cast your vote on %s UTC time.'
                                   % poll.start.strftime('%Y %B %d, %H:%M')))
        return redirect('voting_list_votings')

    # if user has voted, redirect
    if Vote.objects.filter(poll=poll, user=user):
        messages.warning(request, 'You have already cast your vote for this '
                                  'voting. Come back to see the results on '
                                  '%s UTC time.'
                                  % poll.end.strftime('%Y %B %d, %H:%M'))
        return redirect('voting_list_votings')

    # else let the user vote
    range_poll_choice_forms = {}
    radio_poll_choice_forms = {}
    # pack the forms for rendering
    for item in range_poll_choice:
        # Add an extra value, in case a user is in multiple range polls
        # in the save voting, to avoid errors in form fields
        range_poll_choice_form = forms.RangePollChoiceForm(
            data=request.POST or None, extra=range_poll_choice[item])
        range_poll_choice_forms[item] = range_poll_choice_form

    for item in radio_poll_choice:
        answers = [choice.answer for choice in radio_poll_choice[item]]
        radio_poll_choice_form = forms.RadioPollChoiceForm(
            data=request.POST or None, answers=answers)
        radio_poll_choice_forms[item] = radio_poll_choice_form

    if request.method == 'POST':
        range_forms_valid = True
        radio_forms_valid = True
        # Validate all forms
        for item in range_poll_choice_forms:
            if not range_poll_choice_forms[item].is_valid():
                range_forms_valid = False
                break
        for item in radio_poll_choice_forms:
            if not radio_poll_choice_forms[item].is_valid():
                radio_forms_valid = False
        if range_forms_valid and radio_forms_valid:
            # Save data for range poll, use F() to
            # avoid race conditions
            for range_poll in range_poll_choice_forms:
                cdata_range_form = (range_poll_choice_forms[range_poll]
                                    .cleaned_data)
                for data in cdata_range_form:
                    choice_id = data.split('__')[0]
                    for choice in range_poll_choice[range_poll]:
                        if long(choice_id) == choice.id:
                            nominee_votes = int(cdata_range_form[data])
                            RangePollChoice.objects.filter(**{
                                'pk': choice.id
                            }).update(votes=F('votes')+nominee_votes)

            # Save data for radio poll
            for radio_poll in radio_poll_choice_forms:
                cdata_radio_poll = (radio_poll_choice_forms[radio_poll]
                                    .cleaned_data)
                for data in cdata_radio_poll:
                    for choice in radio_poll_choice[radio_poll]:
                        if choice.answer == data:
                            RadioPollChoice.objects.filter(**{
                                'pk': choice.id
                            }).update(votes=F('votes')+1)

            # User voted for this poll
            vote = Vote(user=user, poll=poll)
            vote.save()

            return redirect('voting_list_votings')

    data['range_poll_choice_forms'] = range_poll_choice_forms
    data['radio_poll_choice_forms'] = radio_poll_choice_forms

    return render(request, 'vote_voting.html', data)
