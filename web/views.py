"""Views for the UI prototype.

Each view renders one screen of the design with the sample content from
`demo_data`. They stay deliberately thin so swapping the sample dictionaries
for real querysets later does not touch the templates.
"""

from django.http import Http404
from django.shortcuts import redirect, render
from django.urls import reverse

from . import demo_data


def _segments(done, total):
    """Progress bar as a list of filled/empty segments the template can loop."""
    return [i < done for i in range(total)]


def _shell(active_tab=''):
    """Context every screen needs: the user, the trip and the active tab."""
    return {
        'user_profile': demo_data.USER,
        'trip': demo_data.TRIP,
        'active_tab': active_tab,
    }


def trips(request):
    context = _shell(active_tab='trips')
    context.update({
        'nav_section': 'trips',
        'other_trips': demo_data.OTHER_TRIPS,
        'next_decision': demo_data.NEXT_DECISION,
        'trip_progress': _segments(
            demo_data.TRIP['decisions_settled'],
            demo_data.TRIP['decisions_total'],
        ),
        'vote_progress': _segments(
            demo_data.NEXT_DECISION['voted'],
            demo_data.NEXT_DECISION['voters'],
        ),
    })
    return render(request, 'web/trips.html', context)


def trip_overview(request, slug):
    context = _shell(active_tab='overview')
    context.update({
        'nav_section': 'trips',
        'next_decision': demo_data.NEXT_DECISION,
        'trip_progress': _segments(
            demo_data.TRIP['decisions_settled'],
            demo_data.TRIP['decisions_total'],
        ),
    })
    return render(request, 'web/trip_overview.html', context)


def decision(request, slug, decision_slug):
    try:
        data = demo_data.DECISIONS[decision_slug]
    except KeyError:
        raise Http404('Unknown decision')

    context = _shell(active_tab='decisions')
    context.update({
        'nav_section': 'trips',
        'decision': data,
        'decisions': demo_data.DECISIONS,
        'decision_order': demo_data.DECISION_ORDER,
        'vote_progress': _segments(data['voted'], data['voters']),
        'score_range': [1, 2, 3, 4, 5],
    })
    return render(request, 'web/decision_%s.html' % decision_slug, context)


def itinerary(request, slug):
    context = _shell(active_tab='itinerary')
    context.update({
        'nav_section': 'trips',
        'itinerary': demo_data.ITINERARY,
        'view': 'list',
    })
    return render(request, 'web/itinerary.html', context)


def new_trip(request, step='basics'):
    """The organizer's create-a-trip flow (FR-03 .. FR-06), one step per page."""
    slugs = [s['slug'] for s in demo_data.NEW_TRIP_STEPS]
    if step not in slugs:
        raise Http404('Unknown step')
    index = slugs.index(step)

    if request.method == 'POST':
        # Nothing is saved yet - the models arrive with the next story. The
        # redirect is here so the flow can be clicked through end to end.
        if index + 1 < len(slugs):
            return redirect('web:new_trip_step', step=slugs[index + 1])
        return redirect('web:trip_overview', slug=demo_data.TRIP['slug'])

    steps = []
    for i, data in enumerate(demo_data.NEW_TRIP_STEPS):
        steps.append(dict(
            data,
            number=i + 1,
            is_done=i < index,
            is_current=i == index,
        ))

    context = _shell()
    context.update({
        'nav_section': 'trips',
        'steps': steps,
        'step': steps[index],
        'step_number': index + 1,
        'step_total': len(slugs),
        'prev_slug': slugs[index - 1] if index else None,
        'draft': demo_data.DRAFT_TRIP,
        'summary': [dict(item, filled=item['step'] < index)
                    for item in demo_data.DRAFT_SUMMARY],
    })
    return render(request, 'web/new_trip_%s.html' % step, context)


def styleguide(request):
    """Every component on one page, for reviewing the CSS modules on their own."""
    context = _shell()
    context.update({
        'nav_section': '',
        'score_range': [1, 2, 3, 4, 5],
        'vote_progress': _segments(4, 6),
    })
    return render(request, 'web/styleguide.html', context)


def _chain(trip_slug):
    """The decision chain with each item pointing at the screen that moves it."""
    routes = {
        'decision': lambda item: reverse('web:decision',
                                         args=[trip_slug, item['slug']]),
        'overview': lambda item: reverse('web:trip_overview', args=[trip_slug]),
        'build': lambda item: reverse('web:itinerary_build', args=[trip_slug]),
    }
    return [dict(item, url=routes[item['route']](item))
            for item in demo_data.DECISION_CHAIN]


def decisions(request, slug):
    """Every decision between here and an itinerary, in order."""
    chain = _chain(slug)
    context = _shell(active_tab='decisions')
    context.update({
        'nav_section': 'trips',
        'chain': chain,
        'settled_count': sum(1 for i in chain if i['state'] == 'settled'),
        'open_count': sum(1 for i in chain if i['state'] == 'open'),
        'pending_proposals': len(demo_data.PROPOSALS['pending']),
        'trip_progress': _segments(
            demo_data.TRIP['decisions_settled'],
            demo_data.TRIP['decisions_total'],
        ),
    })
    return render(request, 'web/decisions_index.html', context)


def propose(request, slug, kind):
    """Suggest a destination or an activity to the group (FR-10, FR-11)."""
    try:
        form = demo_data.PROPOSE_FORMS[kind]
    except KeyError:
        raise Http404('Unknown proposal kind')

    if request.method == 'POST':
        return redirect('web:decisions', slug=slug)

    context = _shell(active_tab='decisions')
    context.update({'nav_section': 'trips', 'propose': form})
    return render(request, 'web/propose_%s.html' % kind, context)


def proposals(request, slug):
    """The organizer's queue of things to approve or reject (FR-13)."""
    context = _shell(active_tab='decisions')
    context.update({
        'nav_section': 'trips',
        'proposals': demo_data.PROPOSALS,
    })
    return render(request, 'web/proposals.html', context)


def close_vote(request, slug, decision_slug):
    """Locking a vote is irreversible (FR-18, R-10), so it gets its own screen."""
    if decision_slug not in demo_data.DECISIONS:
        raise Http404('Unknown decision')

    if request.method == 'POST':
        return redirect('web:constraints', slug=slug)

    close = demo_data.CLOSE_VOTE
    context = _shell(active_tab='decisions')
    context.update({
        'nav_section': 'trips',
        'close': close,
        'vote_progress': _segments(close['voted'], close['voters']),
    })
    return render(request, 'web/close_vote.html', context)


def constraints(request, slug):
    """What the build has to respect before it runs (FR-21)."""
    if request.method == 'POST':
        return redirect('web:itinerary_build', slug=slug)

    context = _shell(active_tab='decisions')
    context.update({
        'nav_section': 'trips',
        'constraints': demo_data.CONSTRAINTS,
    })
    return render(request, 'web/constraints.html', context)


def itinerary_build(request, slug):
    """The generated day, with a reason per activity (FR-20, FR-22, FR-25)."""
    if request.method == 'POST':
        return redirect('web:itinerary', slug=slug)

    context = _shell(active_tab='itinerary')
    context.update({
        'nav_section': 'trips',
        'build': demo_data.BUILD,
    })
    return render(request, 'web/itinerary_build.html', context)


def join(request, token, mode='signup'):
    """The invite link (FR-07), with the account step it needs (FR-01, FR-02).

    `mode` picks between creating an account and signing in; both land in the
    same place.
    """
    if mode not in ('signup', 'signin'):
        raise Http404('Unknown mode')

    if request.method == 'POST':
        return redirect('web:join_welcome', token=token)

    other = 'signin' if mode == 'signup' else 'signup'
    alt = ('web:join_signin', [token]) if other == 'signin' else ('web:join', [token])

    context = {
        'trip': demo_data.TRIP,
        'join': demo_data.JOIN,
        'mode': mode,
        'variant': demo_data.JOIN[mode],
        'alt_url': reverse(alt[0], args=alt[1]),
    }
    return render(request, 'web/join.html', context)


def join_expired(request):
    """A revoked or replaced link (NFR-02) is a dead end, not an error page."""
    return render(request, 'web/join_expired.html',
                  {'expired': demo_data.JOIN['expired']})


def join_welcome(request, token):
    """The moment after joining: what the group is already waiting on."""
    return render(request, 'web/join_welcome.html', {
        'trip': demo_data.TRIP,
        'welcome': demo_data.JOIN['welcome'],
    })


def share_manage(request, slug):
    """Make, inspect or revoke the read-only link (FR-09, NFR-02)."""
    context = _shell(active_tab='itinerary')
    context.update({
        'nav_section': 'trips',
        'share': demo_data.SHARE,
    })
    return render(request, 'web/share_manage.html', context)


def share_view(request, token):
    """What a visitor sees: the approved itinerary, and nothing else (R-06)."""
    return render(request, 'web/share_view.html',
                  {'shared': demo_data.SHARED_ITINERARY})


def share_expired(request):
    """A revoked link shows the visitor nothing about the trip."""
    return render(request, 'web/share_expired.html',
                  {'expired': demo_data.SHARE['expired']})


def itinerary_map(request, slug):
    """The same day, drawn: the stay, the stops and the line between them."""
    context = _shell(active_tab='itinerary')
    context.update({
        'nav_section': 'trips',
        'itinerary': demo_data.ITINERARY,
        'map': demo_data.ITINERARY_MAP,
        'view': 'map',
    })
    return render(request, 'web/itinerary_map.html', context)


def money(request, slug):
    """What the trip has cost and where your share stands (FR-28)."""
    context = _shell(active_tab='money')
    context.update({
        'nav_section': 'trips',
        'money': demo_data.MONEY,
        'expenses': demo_data.EXPENSES,
    })
    return render(request, 'web/money.html', context)


def expense_new(request, slug):
    """Record something you paid for, and who it was for (FR-27)."""
    if request.method == 'POST':
        return redirect('web:money', slug=slug)

    context = _shell(active_tab='money')
    context.update({
        'nav_section': 'trips',
        'expense': demo_data.NEW_EXPENSE,
    })
    return render(request, 'web/expense_new.html', context)


def balances(request, slug):
    """Who owes whom, and the fewest payments that settle it (FR-29)."""
    context = _shell(active_tab='money')
    context.update({
        'nav_section': 'trips',
        'balances': demo_data.BALANCES,
        'money': demo_data.MONEY,
    })
    return render(request, 'web/balances.html', context)
