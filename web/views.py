"""Views for the UI prototype.

Each view renders one screen of the design using database-backed context.
"""

import hashlib
from urllib.parse import urlencode

from django.conf import settings
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_not_required
from django.http import Http404
from django.shortcuts import redirect, render, resolve_url
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from trips.models import ReadOnlyShareLink, Trip, TripInvitation, TripParticipant

from .db_context import (
    balances_context,
    build_context,
    constraints_context,
    create_share_token,
    itinerary_context,
    money_context,
    trip_context,
    trip_for_slug,
)
from .forms import LoginForm, RegisterForm
from .ui_data import ui


def _segments(done, total):
    """Progress bar as a list of filled/empty segments the template can loop."""
    return [i < done for i in range(total)]


def _shell(active_tab=''):
    """Context every screen needs, backed by the seeded database."""
    trip = Trip.objects.order_by('id').first()
    if trip is None:
        raise Http404('No trips found. Run seed_demo_data first.')
    return {
        'trip': trip_context(trip),
        'active_tab': active_tab,
    }


def _shell_for_trip(active_tab, trip):
    return {
        'trip': trip_context(trip),
        'active_tab': active_tab,
    }


AUTH_VARIANTS = {
    'signin': {
        'eyebrow': 'Welcome back',
        'title': 'Sign in',
        'lede': 'Pick up where your group left off.',
        'submit': 'Sign in',
        'alt_text': 'New to Trip Sync?',
        'alt_link': 'Create an account',
    },
    'signup': {
        'eyebrow': 'Get started',
        'title': 'Create an account',
        'lede': 'Plan trips with friends: vote, build the days, split the costs.',
        'submit': 'Create account',
        'alt_text': 'Already have an account?',
        'alt_link': 'Sign in',
    },
}


def _safe_next(request):
    """The page to return to after signing in, if it is one of ours."""
    target = request.POST.get('next') or request.GET.get('next') or ''
    if url_has_allowed_host_and_scheme(
        target,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return target
    return ''


def _account_form(request, mode):
    """The bound sign-in or sign-up form for this request."""
    data = request.POST if request.method == 'POST' else None
    if mode == 'signup':
        return RegisterForm(data)
    return LoginForm(request, data)


def _complete_account(request, form, mode):
    """Create or authenticate the user behind a valid form and log them in."""
    user = form.save() if mode == 'signup' else form.user
    login(request, user, backend='django.contrib.auth.backends.ModelBackend')
    return user


def _auth_page(request, mode):
    if request.user.is_authenticated:
        return redirect(settings.LOGIN_REDIRECT_URL)

    form = _account_form(request, mode)
    next_url = _safe_next(request)
    if request.method == 'POST' and form.is_valid():
        _complete_account(request, form, mode)
        return redirect(next_url or resolve_url(settings.LOGIN_REDIRECT_URL))

    alt = reverse('web:register' if mode == 'signin' else 'web:login')
    if next_url:
        alt += '?' + urlencode({'next': next_url})
    return render(request, 'web/auth.html', {
        'form': form,
        'mode': mode,
        'variant': AUTH_VARIANTS[mode],
        'next': next_url,
        'alt_url': alt,
    })


@login_not_required
def login_view(request):
    """Sign in with email and password (FR-02)."""
    return _auth_page(request, 'signin')


@login_not_required
def register_view(request):
    """Create an account (FR-01) and sign straight in."""
    return _auth_page(request, 'signup')


@require_POST
def logout_view(request):
    logout(request)
    return redirect(settings.LOGOUT_REDIRECT_URL)


def trips(request):
    trip = Trip.objects.order_by('id').first()
    context = _shell_for_trip('trips', trip) if trip else _shell('trips')
    context.update({
        'nav_section': 'trips',
        'other_trips': [
            {
                'slug': other.slug,
                'name': other.name,
                'meta': f'{other.departure_date:%b} {other.departure_date.day}–'
                        f'{other.return_date.day} · {other.participants.count()} friends',
                'status': 'Planning',
                'photo': other.final_destination.city.lower()
                if other.final_destination else 'default',
            }
            for other in Trip.objects.exclude(pk=trip.pk).prefetch_related(
                'participants',
                'final_destination',
            )
        ] if trip else [],
        'next_decision': ui.NEXT_DECISION,
        'trip_progress': _segments(
            ui.TRIP['decisions_settled'],
            ui.TRIP['decisions_total'],
        ),
        'vote_progress': _segments(
            ui.NEXT_DECISION['voted'],
            ui.NEXT_DECISION['voters'],
        ),
    })
    return render(request, 'web/trips.html', context)


def trip_overview(request, slug):
    context = _shell_for_trip('overview', trip_for_slug(slug))
    context.update({
        'nav_section': 'trips',
        'next_decision': ui.NEXT_DECISION,
        'trip_progress': _segments(
            ui.TRIP['decisions_settled'],
            ui.TRIP['decisions_total'],
        ),
    })
    return render(request, 'web/trip_overview.html', context)


def decision(request, slug, decision_slug):
    trip = trip_for_slug(slug)
    try:
        data = ui.DECISIONS[decision_slug]
    except KeyError:
        raise Http404('Unknown decision')

    context = _shell_for_trip('decisions', trip)
    context.update({
        'nav_section': 'trips',
        'decision': data,
        'decisions': ui.DECISIONS,
        'decision_order': ui.DECISION_ORDER,
        'vote_progress': _segments(data['voted'], data['voters']),
        'score_range': [1, 2, 3, 4, 5],
    })
    return render(request, 'web/decision_%s.html' % decision_slug, context)


def itinerary(request, slug):
    trip = trip_for_slug(slug)
    context = _shell_for_trip('itinerary', trip)
    context.update({
        'nav_section': 'trips',
        'itinerary': itinerary_context(trip),
        'view': 'list',
    })
    return render(request, 'web/itinerary.html', context)


def new_trip(request, step='basics'):
    """The organizer's create-a-trip flow (FR-03 .. FR-06), one step per page."""
    slugs = [s['slug'] for s in ui.NEW_TRIP_STEPS]
    if step not in slugs:
        raise Http404('Unknown step')
    index = slugs.index(step)

    if request.method == 'POST':
        # Nothing is saved yet - the models arrive with the next story. The
        # redirect is here so the flow can be clicked through end to end.
        if index + 1 < len(slugs):
            return redirect('web:new_trip_step', step=slugs[index + 1])
        return redirect('web:trip_overview', slug=ui.TRIP['slug'])

    steps = []
    for i, data in enumerate(ui.NEW_TRIP_STEPS):
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
        'draft': ui.DRAFT_TRIP,
        'summary': [dict(item, filled=item['step'] < index)
                    for item in ui.DRAFT_SUMMARY],
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
            for item in ui.DECISION_CHAIN]


def decisions(request, slug):
    """Every decision between here and an itinerary, in order."""
    chain = _chain(slug)
    context = _shell(active_tab='decisions')
    context.update({
        'nav_section': 'trips',
        'chain': chain,
        'settled_count': sum(1 for i in chain if i['state'] == 'settled'),
        'open_count': sum(1 for i in chain if i['state'] == 'open'),
        'pending_proposals': len(ui.PROPOSALS['pending']),
        'trip_progress': _segments(
            ui.TRIP['decisions_settled'],
            ui.TRIP['decisions_total'],
        ),
    })
    return render(request, 'web/decisions_index.html', context)


def propose(request, slug, kind):
    """Suggest a destination or an activity to the group (FR-10, FR-11)."""
    try:
        form = ui.PROPOSE_FORMS[kind]
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
        'proposals': ui.PROPOSALS,
    })
    return render(request, 'web/proposals.html', context)


def close_vote(request, slug, decision_slug):
    """Locking a vote is irreversible (FR-18, R-10), so it gets its own screen."""
    if decision_slug not in ui.DECISIONS:
        raise Http404('Unknown decision')

    if request.method == 'POST':
        return redirect('web:constraints', slug=slug)

    close = ui.CLOSE_VOTE
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
    trip = trip_for_slug(slug)
    context = _shell_for_trip('decisions', trip)
    context.update({
        'nav_section': 'trips',
        'constraints': constraints_context(trip),
    })
    return render(request, 'web/constraints.html', context)


def itinerary_build(request, slug):
    """The generated day, with a reason per activity (FR-20, FR-22, FR-25)."""
    if request.method == 'POST':
        return redirect('web:itinerary', slug=slug)

    trip = trip_for_slug(slug)
    context = _shell_for_trip('itinerary', trip)
    context.update({
        'nav_section': 'trips',
        'build': build_context(trip),
    })
    return render(request, 'web/itinerary_build.html', context)


def _join_trip(token, user):
    """Add the user to the trip the invite link belongs to, if it is live."""
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    invitation = TripInvitation.objects.filter(token_hash=token_hash).first()
    if invitation is not None and invitation.is_active:
        TripParticipant.objects.get_or_create(trip=invitation.trip, user=user)


@login_not_required
def join(request, token, mode='signup'):
    """The invite link (FR-07), with the account step it needs (FR-01, FR-02).

    `mode` picks between creating an account and signing in; both land in the
    same place.
    """
    if mode not in ('signup', 'signin'):
        raise Http404('Unknown mode')

    form = _account_form(request, mode)
    if request.method == 'POST' and form.is_valid():
        user = _complete_account(request, form, mode)
        _join_trip(token, user)
        return redirect('web:join_welcome', token=token)

    other = 'signin' if mode == 'signup' else 'signup'
    alt = ('web:join_signin', [token]) if other == 'signin' else ('web:join', [token])

    context = {
        'form': form,
        'trip': ui.TRIP,
        'join': ui.JOIN,
        'mode': mode,
        'variant': ui.JOIN[mode],
        'alt_url': reverse(alt[0], args=alt[1]),
    }
    return render(request, 'web/join.html', context)


@login_not_required
def join_expired(request):
    """A revoked or replaced link (NFR-02) is a dead end, not an error page."""
    return render(request, 'web/join_expired.html',
                  {'expired': ui.JOIN['expired']})


@login_not_required
def join_welcome(request, token):
    """The moment after joining: what the group is already waiting on."""
    return render(request, 'web/join_welcome.html', {
        'trip': ui.TRIP,
        'welcome': ui.JOIN['welcome'],
    })


def share_manage(request, slug):
    """Make, inspect or revoke the read-only link (FR-09, NFR-02)."""
    trip = trip_for_slug(slug)
    token = create_share_token(trip, trip.organizer) if request.method == 'POST' else None
    context = _shell_for_trip('itinerary', trip)
    context.update({
        'nav_section': 'trips',
        'share': {
            'title': 'Share the itinerary',
            'lede': 'A read-only view for anyone with the link.',
            'token': token or '',
            'link': f'/share/{token}/' if token else '',
            'created': 'Created just now' if token else 'No new link generated',
            'views': 'Read-only access',
            'shown': ['Final destination', 'Approved itinerary'],
            'hidden': ['Votes', 'Expenses'],
            'revoke_note': 'The token is shown only once when the link is created.',
        },
    })
    return render(request, 'web/share_manage.html', context)


@login_not_required
def share_view(request, token):
    """What a visitor sees: the approved itinerary, and nothing else (R-06)."""
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    link = ReadOnlyShareLink.objects.select_related('trip').filter(
        token_hash=token_hash,
    ).first()
    if link is None or not link.is_active:
        return redirect('web:share_expired')
    return render(request, 'web/share_view.html', {
        'shared': {
            'trip': trip_context(link.trip),
            'itinerary': itinerary_context(link.trip),
        },
    })


@login_not_required
def share_expired(request):
    """A revoked link shows the visitor nothing about the trip."""
    return render(request, 'web/share_expired.html',
                  {'expired': ui.SHARE['expired']})


def itinerary_map(request, slug):
    """The same day, drawn: the stay, the stops and the line between them."""
    trip = trip_for_slug(slug)
    context = _shell_for_trip('itinerary', trip)
    context.update({
        'nav_section': 'trips',
        'itinerary': itinerary_context(trip),
        'map': ui.ITINERARY_MAP,
        'view': 'map',
    })
    return render(request, 'web/itinerary_map.html', context)


def money(request, slug):
    """What the trip has cost and where your share stands (FR-28)."""
    trip = trip_for_slug(slug)
    context = _shell_for_trip('money', trip)
    context.update({
        'nav_section': 'trips',
        **money_context(trip),
    })
    return render(request, 'web/money.html', context)


def expense_new(request, slug):
    """Record something you paid for, and who it was for (FR-27)."""
    if request.method == 'POST':
        return redirect('web:money', slug=slug)

    context = _shell_for_trip('money', trip_for_slug(slug))
    context.update({
        'nav_section': 'trips',
        'expense': ui.NEW_EXPENSE,
    })
    return render(request, 'web/expense_new.html', context)


def balances(request, slug):
    """Who owes whom, and the fewest payments that settle it (FR-29)."""
    trip = trip_for_slug(slug)
    context = _shell_for_trip('money', trip)
    context.update({
        'nav_section': 'trips',
        'balances': balances_context(trip),
        **money_context(trip),
    })
    return render(request, 'web/balances.html', context)
