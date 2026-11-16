"""Views for the UI prototype.

Each view renders one screen of the design using database-backed context.
"""

from datetime import date
from decimal import ROUND_HALF_UP, Decimal
from urllib.parse import urlencode

from django.conf import settings
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_not_required
from django.core.mail import send_mail
from django.db import transaction
from django.http import Http404
from django.shortcuts import redirect, render, resolve_url
from django.urls import reverse
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from trips.models import (
    Destination,
    ProposalStatus,
    ReadOnlyShareLink,
    Trip,
    TripInvitation,
    TripParticipant,
)

from .db_context import (
    balances_context,
    build_context,
    constraints_context,
    create_invitation,
    create_share_token,
    itinerary_context,
    money_context,
    short_date,
    token_hash,
    trip_context,
    trip_for_slug,
    user_initials,
)
from .forms import (
    TRIP_CURRENCIES,
    LoginForm,
    RegisterForm,
    TripBasicsForm,
    TripBudgetForm,
    TripDatesForm,
    TripInviteForm,
)
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


def _people(count):
    return f'{count} person' if count == 1 else f'{count} people'


def trips(request):
    """The trips the signed-in user belongs to, newest first (R-04)."""
    my_trips = list(
        request.user.trips
        .select_related('final_destination')
        .prefetch_related('participants')
        .order_by('-created_at')
    )
    featured = my_trips[0] if my_trips else None
    if featured:
        context = _shell_for_trip('trips', featured)
    else:
        context = {'trip': None, 'active_tab': 'trips'}
    context.update({
        'nav_section': 'trips',
        'other_trips': [
            {
                'slug': other.slug,
                'name': other.name,
                'meta': f'{short_date(other.departure_date)}–'
                        f'{short_date(other.return_date)} · '
                        f'{_people(other.participants.count())}',
                'status': 'Organizer' if other.organizer_id == request.user.pk
                else 'Planning',
                'photo': other.final_destination.city.lower()
                if other.final_destination else 'default',
            }
            for other in my_trips[1:]
        ],
        'next_decision': ui.NEXT_DECISION if featured else {},
        'trip_progress': _segments(
            context['trip']['decisions_settled'],
            context['trip']['decisions_total'],
        ) if featured else [],
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


# The create-a-trip flow (FR-03 .. FR-06). The first three steps are kept in
# the session and the trip is created when the budget step is submitted; the
# last step invites people to the trip that now exists.
NEW_TRIP_STEPS = [
    {
        'slug': 'basics',
        'label': 'Basics',
        'title': 'Trip basics',
        'lede': 'A name, and where you\u2019re going if you already know.',
        'next': 'Continue',
    },
    {
        'slug': 'when',
        'label': 'Dates',
        'title': 'When are you going?',
        'lede': 'Pick the days. The length of the trip follows from them.',
        'next': 'Continue',
    },
    {
        'slug': 'budget',
        'label': 'Budget',
        'title': 'The budget',
        'lede': 'What the group is ready to spend on activities, in total.',
        'next': 'Create trip',
    },
    {
        'slug': 'invite',
        'label': 'Invite',
        'title': 'Who\u2019s coming?',
        'lede': 'Invite people by email or send them the group link. '
                'You can come back to this later.',
        'next': 'Done',
    },
]
NEW_TRIP_FORMS = {
    'basics': TripBasicsForm,
    'when': TripDatesForm,
    'budget': TripBudgetForm,
}
NEW_TRIP_DRAFT_KEY = 'new_trip_draft'
# The trip just created by this flow, for the invite step.
NEW_TRIP_CREATED_KEY = 'new_trip_created'


def _parse_date(value):
    try:
        return date.fromisoformat(value or '')
    except (TypeError, ValueError):
        return None


def _trip_span(start, end):
    """'4 days, 3 nights' for two ISO dates, or None if they don't make sense."""
    start, end = _parse_date(start), _parse_date(end)
    if not start or not end or end < start:
        return None
    nights = (end - start).days
    days = nights + 1
    return (f'{days} day{"s" if days != 1 else ""}, '
            f'{nights} night{"s" if nights != 1 else ""}')


def _per_person(total, group_size):
    return (Decimal(total) / int(group_size)).quantize(
        Decimal('0.01'), rounding=ROUND_HALF_UP,
    )


def _draft_values(source):
    """What the step templates show in their fields, plus derived hints."""
    values = {
        'name': '', 'description': '', 'city': '', 'country': '',
        'start': '', 'end': '',
        'budget': '', 'currency': TRIP_CURRENCIES[0], 'group_size': '',
    }
    values.update({k: v for k, v in source.items() if k in values})
    values['currencies'] = TRIP_CURRENCIES
    values['span'] = (_trip_span(values['start'], values['end'])
                      or 'Pick both days to see how long the trip is.')
    budget_form = TripBudgetForm(values)
    if budget_form.is_valid():
        cleaned = budget_form.cleaned_data
        values['per_person'] = (
            f"{_per_person(cleaned['budget'], cleaned['group_size'])} "
            f"{cleaned['currency']} per person"
        )
    return values


def _draft_summary(draft):
    """The 'Your trip so far' rail."""
    start, end = _parse_date(draft.get('start')), _parse_date(draft.get('end'))
    dates = None
    if start and end:
        dates = (f'{short_date(start)} – {short_date(end)}, {end.year} · '
                 f'{_trip_span(draft["start"], draft["end"])}')
    budget = None
    if draft.get('budget') and draft.get('group_size'):
        budget = (f"{draft['budget']} {draft.get('currency', '')} · "
                  f"{_per_person(draft['budget'], draft['group_size'])} per person, "
                  f"{draft['group_size']} people")
    destination = None
    if draft.get('city'):
        destination = f"{draft['city']}, {draft.get('country', '')}"
    elif draft.get('name'):
        destination = 'Not decided: the group will propose and vote'
    return [
        {'label': 'Name', 'value': draft.get('name'), 'pending': 'Not named yet'},
        {'label': 'Destination', 'value': destination, 'pending': 'Not set yet'},
        {'label': 'Dates', 'value': dates, 'pending': 'Not set yet'},
        {'label': 'Budget', 'value': budget, 'pending': 'Not set yet'},
    ]


def _first_invalid_step(draft):
    """Index of the first step whose saved answers don't validate, or None."""
    for index, step in enumerate(NEW_TRIP_STEPS):
        form_class = NEW_TRIP_FORMS.get(step['slug'])
        if form_class and not form_class(draft).is_valid():
            return index
    return None


def _create_trip(user, draft):
    """Write the finished draft to the database. The creator is the organizer."""
    cleaned = {}
    for form_class in NEW_TRIP_FORMS.values():
        form = form_class(draft)
        form.is_valid()
        cleaned.update(form.cleaned_data)
    with transaction.atomic():
        trip = Trip(
            name=cleaned['name'],
            description=cleaned['description'],
            organizer=user,
            departure_date=cleaned['start'],
            return_date=cleaned['end'],
            budget_per_person=_per_person(cleaned['budget'], cleaned['group_size']),
            currency=cleaned['currency'],
        )
        trip.clean()
        # Trip.save() also adds the organizer as a participant.
        trip.save()
        if cleaned['city']:
            # The organizer already knows where: that is the trip's destination.
            trip.final_destination = Destination.objects.create(
                trip=trip,
                city=cleaned['city'],
                country=cleaned['country'],
                status=ProposalStatus.APPROVED,
                created_by=user,
            )
            trip.save(update_fields=['final_destination', 'updated_at'])
    return trip


def new_trip(request, step='basics'):
    """The organizer's create-a-trip flow (FR-03 .. FR-05), one step per page.

    Answers are kept in the session until the last step, then the trip is
    created with the signed-in user as its organizer.
    """
    slugs = [s['slug'] for s in NEW_TRIP_STEPS]
    if step not in slugs:
        raise Http404('Unknown step')
    if step == 'invite':
        return _new_trip_invite(request)
    index = slugs.index(step)
    form_class = NEW_TRIP_FORMS[step]
    draft = request.session.get(NEW_TRIP_DRAFT_KEY, {})

    # No skipping ahead past a step that hasn't been filled in yet.
    first_invalid = _first_invalid_step(draft)
    if first_invalid is not None and index > first_invalid:
        return redirect('web:new_trip_step', step=slugs[first_invalid])

    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            for field, value in form.cleaned_data.items():
                draft[field] = '' if value is None else str(value)
            request.session[NEW_TRIP_DRAFT_KEY] = draft
            if slugs[index + 1] in NEW_TRIP_FORMS:
                return redirect('web:new_trip_step', step=slugs[index + 1])

            first_invalid = _first_invalid_step(draft)
            if first_invalid is not None:
                # E.g. the start date went by while the draft sat in the session.
                return redirect('web:new_trip_step', step=slugs[first_invalid])
            trip = _create_trip(request.user, draft)
            del request.session[NEW_TRIP_DRAFT_KEY]
            request.session[NEW_TRIP_CREATED_KEY] = {'slug': trip.slug, 'draft': draft}
            return redirect('web:new_trip_step', step='invite')
        values = _draft_values(request.POST.dict())
    else:
        # Show earlier answers, and their errors if they no longer hold.
        has_answers = any(field in draft for field in form_class.base_fields)
        form = form_class(draft) if has_answers else form_class()
        values = _draft_values(draft)

    return _render_new_trip_step(request, index, {
        'form': form,
        'draft': values,
        'summary_source': draft,
    })


def _render_new_trip_step(request, index, extra):
    steps = [
        dict(data, number=i + 1, is_done=i < index, is_current=i == index)
        for i, data in enumerate(NEW_TRIP_STEPS)
    ]
    slugs = [s['slug'] for s in NEW_TRIP_STEPS]
    context = {
        'active_tab': '',
        'nav_section': 'trips',
        'steps': steps,
        'step': steps[index],
        'step_number': index + 1,
        'step_total': len(steps),
        'prev_slug': slugs[index - 1] if index else None,
        'summary': [dict(item, filled=bool(item['value']))
                    for item in _draft_summary(extra.pop('summary_source'))],
    }
    context.update(extra)
    return render(request, 'web/new_trip_%s.html' % slugs[index], context)


def _send_invite_email(request, trip, email, token):
    inviter = request.user.get_full_name() or request.user.email
    link = request.build_absolute_uri(reverse('web:join', args=[token]))
    send_mail(
        subject=f'{inviter} invited you to {trip.name} on Trip Sync',
        message=(
            f'{inviter} is planning "{trip.name}" and wants you along.\n\n'
            f'Join the group here: {link}\n'
        ),
        from_email=None,
        recipient_list=[email],
        fail_silently=True,
    )


def _new_trip_invite(request):
    """Step 4 (FR-06): invite people to the trip this flow just created.

    Emails get their own invitation each. The group link is one more
    invitation without an email; making a new one revokes the old (NFR-02).
    Its raw token is shown once, when it is made, and only its hash is kept.
    Only the organizer who created the trip gets here.
    """
    created = request.session.get(NEW_TRIP_CREATED_KEY) or {}
    trip = Trip.objects.filter(
        slug=created.get('slug'), organizer=request.user,
    ).first()
    if trip is None:
        return redirect('web:new_trip')

    def active_group_links():
        return trip.invitations.filter(
            email='', revoked_at__isnull=True, accepted_at__isnull=True,
        )

    # The raw group-link token is never stored, not even in the session: like
    # the read-only link, it is shown once, on the response that creates it.
    new_link_token = None
    form = TripInviteForm(trip=trip, inviter=request.user)
    if request.method == 'POST':
        action = request.POST.get('action', 'add')
        if action == 'done':
            del request.session[NEW_TRIP_CREATED_KEY]
            return redirect('web:trip_overview', slug=trip.slug)
        if action == 'new_link':
            # Rendered straight away, not redirected: this response is the one
            # time the new link is shown.
            active_group_links().update(revoked_at=timezone.now())
            new_link_token = create_invitation(trip, request.user)
        elif action.startswith('remove:'):
            pk = action.partition(':')[2]
            if pk.isdigit():
                trip.invitations.filter(
                    pk=int(pk), revoked_at__isnull=True,
                ).exclude(email='').update(revoked_at=timezone.now())
            return redirect('web:new_trip_step', step='invite')
        else:
            form = TripInviteForm(request.POST, trip=trip, inviter=request.user)
            if form.is_valid():
                email = form.cleaned_data['invite']
                token = create_invitation(trip, request.user, email)
                _send_invite_email(request, trip, email, token)
                return redirect('web:new_trip_step', step='invite')

    if new_link_token is None and not active_group_links().exists():
        new_link_token = create_invitation(trip, request.user)
    members = [user for user in trip.participants.all() if user.pk != request.user.pk]
    member_emails = {user.email.lower() for user in members}
    index = [s['slug'] for s in NEW_TRIP_STEPS].index('invite')
    return _render_new_trip_step(request, index, {
        'form': form,
        'trip_slug': trip.slug,
        'steps_locked': True,
        'skip_url': reverse('web:trip_overview', args=[trip.slug]),
        'invited': [
            invitation for invitation in trip.invitations.filter(
                revoked_at__isnull=True, accepted_at__isnull=True,
            ).exclude(email='').order_by('created_at')
            if invitation.email.lower() not in member_emails
        ],
        'members': members,
        'invite_link': request.build_absolute_uri(
            reverse('web:join', args=[new_link_token]),
        ) if new_link_token else '',
        'summary_source': created.get('draft', {}),
    })


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


def _live_invitation(token):
    """The invitation behind a link, if it can still be used."""
    invitation = TripInvitation.objects.select_related(
        'trip', 'created_by',
    ).filter(token_hash=token_hash(token)).first()
    if invitation is None or not invitation.is_active:
        return None
    return invitation


def _join_trip(token, user):
    """Add the user to the trip the invite link belongs to, if it is live."""
    invitation = _live_invitation(token)
    if invitation is not None:
        TripParticipant.objects.get_or_create(trip=invitation.trip, user=user)


def _join_context(invitation):
    inviter = invitation.created_by
    return dict(
        ui._join(invitation.trip),
        inviter={
            'name': inviter.get_full_name() or inviter.email,
            'initials': user_initials(inviter),
            'role': 'Organizer' if inviter.pk == invitation.trip.organizer_id
            else 'Participant',
        },
    )


@login_not_required
def join(request, token, mode='signup'):
    """The invite link (FR-07), with the account step it needs (FR-01, FR-02).

    `mode` picks between creating an account and signing in; both land in the
    same place.
    """
    if mode not in ('signup', 'signin'):
        raise Http404('Unknown mode')
    invitation = _live_invitation(token)
    if invitation is None:
        return redirect('web:join_expired')

    form = _account_form(request, mode)
    if request.method == 'POST' and form.is_valid():
        user = _complete_account(request, form, mode)
        _join_trip(token, user)
        return redirect('web:join_welcome', token=token)

    other = 'signin' if mode == 'signup' else 'signup'
    alt = ('web:join_signin', [token]) if other == 'signin' else ('web:join', [token])

    join_data = _join_context(invitation)
    context = {
        'form': form,
        'trip': trip_context(invitation.trip),
        'join': join_data,
        'mode': mode,
        'variant': join_data[mode],
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
    invitation = TripInvitation.objects.select_related('trip', 'created_by').filter(
        token_hash=token_hash(token),
    ).first()
    if invitation is None:
        return redirect('web:join_expired')
    return render(request, 'web/join_welcome.html', {
        'trip': trip_context(invitation.trip),
        'welcome': _join_context(invitation)['welcome'],
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
    link = ReadOnlyShareLink.objects.select_related('trip').filter(
        token_hash=token_hash(token),
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
