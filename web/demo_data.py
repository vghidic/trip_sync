"""Static sample content for the UI prototype.

Nothing here touches the database yet: the templates are built against these
dictionaries so the markup and CSS can be reviewed before the models exist.
When the real models land, the views swap these for querysets and the
templates stay as they are.
"""

USER = {'name': 'Vlad', 'initials': 'VG'}

FRIENDS = [
    {'name': 'Vlad', 'initials': 'VG', 'is_me': True},
    {'name': 'Jules', 'initials': 'JU', 'is_me': False},
    {'name': 'Theo', 'initials': 'TH', 'is_me': False},
    {'name': 'Nina', 'initials': 'NI', 'is_me': False},
    {'name': 'Maya', 'initials': 'MA', 'is_me': False},
    {'name': 'Leo', 'initials': 'LE', 'is_me': False},
]

TRIP = {
    'slug': 'lisbon',
    'name': 'Lisbon, with the usuals',
    'destination': 'Lisbon',
    'country': 'Portugal',
    'tagline': 'Six friends. Two nights.',
    'dates': 'Jun 18-20',
    'dates_long': 'Jun 18-20, 2027',
    'dates_note': '2027 · Fri-Sun',
    'countdown': 'In 29 days',
    'budget': '€2,700',
    'budget_note': 'shared budget for the trip',
    'decisions_settled': 4,
    'decisions_total': 7,
    'photo': 'lisbon',
    'friends': FRIENDS,
}

OTHER_TRIPS = [
    {
        'slug': 'margate',
        'name': 'A little Margate escape',
        'meta': 'Aug 6-8 · 4 friends',
        'status': 'Just getting started',
        'photo': 'margate',
    },
]

NEXT_DECISION = {
    'slug': 'stay',
    'kind': 'Stay',
    'title': 'Choose your stay',
    'subtitle': 'Lisbon · Vote by Fri, May 21',
    'due': 'Fri, May 21',
    'voted': 4,
    'voters': 6,
    'note': '2 options within budget',
    'summary': '3 options · 4 of 6 voted',
    'cta': 'Compare 3 stays & vote',
}

DECISIONS = {
    'destination': {
        'slug': 'destination',
        'index': 'Destination · Decision 1 of 3',
        'eyebrow': 'Destination',
        'title': 'Where shall we go?',
        'lede': '',
        'mode': 'yesno',
        'owner': {'name': 'Jules', 'initials': 'JU', 'role': 'organizer'},
        'due': 'Fri, May 7 · 6 pm',
        'voted': 4,
        'voters': 6,
        'waiting_on': 'you and Leo',
        'options': [
            {
                'name': 'Lisbon',
                'country': 'Portugal',
                'photo': 'lisbon',
                'blurb': 'Tiled streets, river views and long dinners in Alfama.',
                'yes': 3, 'no': 1,
                'yes_names': 'Jules, Theo, Maya',
                'my_vote': 'yes',
            },
            {
                'name': 'Porto',
                'country': 'Portugal',
                'photo': 'porto',
                'blurb': 'Douro-side wandering, little wine bars and a slower pace.',
                'yes': 2, 'no': 2,
                'yes_names': 'Jules, Leo',
                'my_vote': 'yes',
            },
            {
                'name': 'Seville',
                'country': 'Spain',
                'photo': 'seville',
                'blurb': 'Orange-tree courtyards, tapas and warm Andalusian nights.',
                'yes': 1, 'no': 3,
                'yes_names': 'Theo',
                'my_vote': 'no',
            },
        ],
    },
    'stay': {
        'slug': 'stay',
        'index': 'Stay · Decision 1 of 3',
        'eyebrow': 'Stay',
        'title': 'Choose your stay',
        'lede': '',
        'meta': 'Jun 18-20 · Shared stay budget',
        'mode': 'pick',
        'owner': {'name': 'Jules', 'initials': 'JU', 'role': 'organizer'},
        'due': 'Fri, May 21 · 6 pm',
        'voted': 4,
        'voters': 6,
        'waiting_on': 'you & Nina',
        'panel_title': 'Casa do Pátio',
        'panel_note': 'Casa do Pátio selected · vote not submitted',
        'panel_cta': 'Vote for Casa do Pátio',
        'panel_foot': 'You can change your vote until the deadline.',
        'options': [
            {
                'name': 'Casa do Pátio', 'photo': 'casa',
                'meta': 'Graça · 3 bedrooms',
                'price': '€888', 'price_note': 'total · 2 nights',
                'badge': 'Within the shared budget', 'badge_tone': 'ok',
                'votes': 3, 'vote_names': 'Jules, Theo, Maya',
                'selected': True, 'flag': 'Selected',
            },
            {
                'name': 'Alfama Loft', 'photo': 'loft',
                'meta': 'Alfama · 3 bedrooms',
                'price': '€936', 'price_note': 'total · 2 nights',
                'badge': 'Within the shared budget', 'badge_tone': 'ok',
                'votes': 1, 'vote_names': 'Leo',
                'selected': False, 'flag': '',
            },
            {
                'name': 'Bairro House', 'photo': 'bairro',
                'meta': 'Príncipe Real · 3 bedrooms',
                'price': '€1,128', 'price_note': 'total · 2 nights',
                'badge': '€192 over the shared budget', 'badge_tone': 'warn',
                'votes': 0, 'vote_names': 'No votes yet',
                'selected': False, 'flag': '',
            },
        ],
    },
    'activities': {
        'slug': 'activities',
        'index': 'Saturday plan · Decision 2 of 3',
        'eyebrow': 'Saturday plan',
        'title': 'A Saturday worth sharing.',
        'lede': 'Lisbon · Saturday, Jun 19, 2027. Score each idea from 1 (not for '
                'me) to 5 (love it). One score per activity.',
        'mode': 'score',
        'owner': {'name': 'Nina', 'initials': 'NI', 'role': 'activities lead'},
        'due': 'Fri, May 28 · 6 pm',
        'voted': 4,
        'voters': 6,
        'waiting_on': 'you & Nina',
        'stats': [
            {'icon': 'wallet', 'label': 'Total group activity budget',
             'value': '€360 total'},
            {'icon': 'clock', 'label': 'Available activity time',
             'value': '6 hours · breaks & travel reserved'},
        ],
        'note': 'Group scores are means of submitted preferences, not a confirmed plan.',
        'panel_title': 'Your Saturday, scored.',
        'panel_note': '4 of 4 activities scored. These are draft preferences, '
                      'not itinerary selections.',
        'panel_cta': 'Submit preferences',
        'panel_foot': 'You can change your vote until Jules, the organizer, closes '
                      'voting. Votes are locked afterward.',
        'options': [
            {
                'name': 'A wander through Alfama',
                'photo': 'alfama', 'cost': '€0 total',
                'duration': '2 hours', 'score': '4.50', 'submitted': 4, 'my_score': 5,
            },
            {
                'name': 'Make your own azulejo',
                'photo': 'azulejo', 'cost': '€180 total',
                'duration': '2 hours', 'score': '4.00', 'submitted': 4, 'my_score': 4,
            },
            {
                'name': 'Saturday sunset sail',
                'photo': 'sail', 'cost': '€210 total',
                'duration': '2 hours', 'score': '4.75', 'submitted': 4, 'my_score': 3,
            },
            {
                'name': 'A pastel de nata pit stop',
                'photo': 'nata', 'cost': '€30 total',
                'duration': '1 hour', 'score': '4.25', 'submitted': 4, 'my_score': 2,
            },
        ],
    },
    'transfers': {
        'slug': 'transfers',
        'index': 'Airport transfers · Decision 3 of 3',
        'eyebrow': 'Airport transfers',
        'title': 'One last bit of getting there.',
        'lede': 'The ride home starts here. Choose one way for all six of us to reach '
                'Lisbon airport on Sunday, Jun 20, 2027.',
        'mode': 'pick',
        'route': {
            'title': 'Rossio meeting point → Lisbon airport · T1',
            'note': 'Planning example: 17:30 flight · aim to arrive by 14:30 '
                    '· local times',
        },
        'meta': 'Pick one option. Prices below are split across 6 friends.',
        'owner': {'name': 'Theo', 'initials': 'TH', 'role': 'transfers lead'},
        'due': 'Fri, Jun 4 · 6 pm',
        'voted': 4,
        'voters': 6,
        'waiting_on': 'you & Nina',
        'panel_title': 'One shared van',
        'panel_note': 'Selected for the group. Your vote has not been submitted yet.',
        'panel_cta': 'Vote for shared van',
        'panel_foot': 'You can change your vote until Jules, the organizer, closes '
                      'voting. Votes are locked afterward.',
        'aside_title': 'A plan, not a booking.',
        'aside_body': 'Only Jules can close voting. Theo will then confirm pickup '
                      'details and check availability with the group before arranging '
                      'anything.',
        'footnote': 'Illustrative prices and journey times, not live quotes. No booking '
                    'or payment is made by voting. Your draft pick is not included in '
                    'the counts.',
        'options': [
            {
                'name': 'One shared van', 'photo': 'van',
                'meta': '6 friends · 1 vehicle',
                'price': '€10', 'price_note': '/ person · one way',
                'total': '€60 group total · estimate',
                'rows': [
                    ('Journey', '25-40 min'),
                    ('Leave Rossio', '13:40'),
                    ('At the airport', '14:05-14:20'),
                ],
                'blurb': 'Together, with room for 6 cabin bags.',
                'votes': 3, 'vote_names': 'Jules, Theo, Maya',
                'selected': True, 'flag': 'Draft pick',
            },
            {
                'name': 'Two taxis', 'photo': 'taxi',
                'meta': '3 friends in each car',
                'price': '€8', 'price_note': '/ person · one way',
                'total': '€48 group total · estimate',
                'rows': [
                    ('Journey', '25-40 min'),
                    ('Leave Rossio', '13:40'),
                    ('At the airport', '14:05-14:20'),
                ],
                'blurb': 'Split into two cars; luggage space varies.',
                'votes': 1, 'vote_names': 'Leo',
                'selected': False, 'flag': '',
            },
            {
                'name': 'Metro together', 'photo': 'metro',
                'meta': 'Walk + metro · 1 change',
                'price': '€3', 'price_note': '/ person · one way',
                'total': '€18 group total · estimate',
                'rows': [
                    ('Journey', '55-65 min'),
                    ('Leave Rossio', '13:10'),
                    ('At the airport', '14:05-14:15'),
                ],
                'blurb': 'Lowest cost; carry bags on stairs and trains.',
                'votes': 0, 'vote_names': 'No votes yet',
                'selected': False, 'flag': '',
            },
        ],
    },
}

DECISION_ORDER = ['destination', 'stay', 'activities', 'transfers']

ITINERARY = {
    'eyebrow': 'Jun 18-20 · Lisbon',
    'title': 'Proposed itinerary.',
    'days': [
        {'num': '18', 'weekday': 'Fri', 'note': '2 plans', 'active': True},
        {'num': '19', 'weekday': 'Sat', 'note': 'Open day', 'active': False},
        {'num': '20', 'weekday': 'Sun', 'note': 'Travel day', 'active': False},
    ],
    'day_title': 'Friday, June 18',
    'day_status': 'Confirmed',
    'entries': [
        {
            'time': '14:30', 'title': 'Hello, Lisbon',
            'place': 'Santa Apolónia station',
            'meta': 'All 6 arriving · Jules coordinating',
            'icon': 'train',
        },
        {
            'time': '19:30', 'title': 'First-night dinner',
            'place': 'Taberna Sal Grosso · Alfama',
            'meta': 'Booked by Theo · Table for 6',
            'icon': 'dinner',
        },
    ],
    'nudge': {
        'title': 'Your hotel is still a decision.',
        'note': 'Vote on 3 stays · Due Fri, May 21',
    },
}


# ---------------------------------------------------------------------------
# Creating a trip (FR-03 .. FR-06, R-05, R-11).
#
# One step per thing the organizer has to decide, so the flow reads like the
# rest of the app: a single question at a time.

NEW_TRIP_STEPS = [
    {
        'slug': 'basics',
        'label': 'The basics',
        'title': 'Start',
        'next': 'Continue to dates',
    },
    {
        'slug': 'when',
        'label': 'When',
        'title': 'When are we going?',
        'next': 'Continue to budget',
    },
    {
        'slug': 'budget',
        'label': 'Budget',
        'title': 'What can everyone spend?',
        'lede': 'One shared pot, split equally. Nothing the group picks will '
                'add up to more than this.',
        'next': 'Continue to friends',
    },
    {
        'slug': 'invite',
        'label': 'Friends',
        'title': 'Who’s coming?',
        'lede': 'Invite by email, or send the link to the group chat. They '
                'join as participants and can propose and vote straight away.',
        'next': 'Create trip',
    },
]

DRAFT_TRIP = {
    'name': 'A weekend with the usuals',
    'description': 'Two nights somewhere warm, decided together. Nobody wants '
                   'to be the one organising it this time.',
    'start': '2027-06-18',
    'end': '2027-06-20',
    'span': '2 nights · Fri to Sun',
    'hours_per_day': 6,
    'hour_choices': [
        {'value': 4, 'label': '4 hours'},
        {'value': 6, 'label': '6 hours'},
        {'value': 8, 'label': '8 hours'},
    ],
    'budget': '2700',
    'group_size': '6',
    'currency': 'EUR',
    'currencies': ['€ EUR', '£ GBP', 'lei RON'],
    'invites': [
        'jules@example.com',
        'theo@example.com',
        'nina@example.com',
        'maya@example.com',
        'leo@example.com',
    ],
    'invite_link': 'tripsync.app/join/7f3b-91ac-24de',
    'invite_token': '7f3b-91ac-24de',
}

DRAFT_SUMMARY = [
    {'label': 'Name', 'value': DRAFT_TRIP['name'],
     'pending': 'Not named yet', 'step': 0},
    {'label': 'Dates', 'value': 'Jun 18–20, 2027 · 2 nights',
     'pending': 'Not set yet', 'step': 1},
    {'label': 'Plans per day', 'value': '6 hours',
     'pending': 'Not set yet', 'step': 1},
    {'label': 'Budget', 'value': '€2,700 shared trip budget',
     'pending': 'Not set yet', 'step': 2},
    {'label': 'Friends', 'value': '5 invited · 6 in the group',
     'pending': 'Just you so far', 'step': 3},
]


# ---------------------------------------------------------------------------
# The chain of decisions between creating a trip and having an itinerary.
#
# Order follows the flow in the requirements: propose (FR-10, FR-11), the
# organizer approves (FR-13), the group votes (FR-14, FR-15), the organizer
# closes voting (FR-18) and sets constraints (FR-21), then the itinerary is
# generated (FR-19, FR-20) with a reason per activity (FR-22) and approved
# (FR-25).

DECISION_CHAIN = [
    {
        'number': 1,
        'slug': 'destination',
        'kind': 'Destination',
        'title': 'Where shall we go?',
        'blurb': 'Everyone says yes or no. Most yeses wins; a tie is the '
                 'organizer’s call.',
        'state': 'settled',
        'status': 'Settled',
        'result': 'Lisbon · 3 of 4 yes',
        'meta': 'Closed Fri, May 7 · Jules',
        'cta': 'See the vote',
        'route': 'decision',
    },
    {
        'number': 2,
        'slug': 'frame',
        'kind': 'Dates & budget',
        'title': 'The shape of the weekend',
        'blurb': 'Set by the organizer, not voted on. Everything else is '
                 'planned inside it.',
        'state': 'settled',
        'status': 'Settled',
        'result': 'Jun 18–20 · €2,700 · 6 hours a day',
        'meta': 'Set by Jules',
        'cta': 'View',
        'route': 'overview',
    },
    {
        'number': 3,
        'slug': 'stay',
        'kind': 'Stay',
        'title': 'Choose your stay',
        'blurb': 'One place for all six of us. Pick the one you want.',
        'state': 'open',
        'status': 'Needs your vote',
        'result': '',
        'meta': '4 of 6 voted · Due Fri, May 21 · Jules',
        'cta': 'Vote on 3 stays',
        'route': 'decision',
    },
    {
        'number': 4,
        'slug': 'activities',
        'kind': 'Saturday plan',
        'title': 'A Saturday worth sharing.',
        'blurb': 'Score each idea 1 to 5. The group score is the mean of the '
                 'scores submitted.',
        'state': 'open',
        'status': 'Needs your scores',
        'result': '',
        'meta': '4 of 6 voted · Due Fri, May 28 · Nina',
        'cta': 'Score 4 activities',
        'route': 'decision',
    },
    {
        'number': 5,
        'slug': 'transfers',
        'kind': 'Airport transfers',
        'title': 'One last bit of getting there.',
        'blurb': 'One way home for all six of us.',
        'state': 'open',
        'status': 'Needs your vote',
        'result': '',
        'meta': '4 of 6 voted · Due Fri, Jun 4 · Theo',
        'cta': 'Vote on 3 options',
        'route': 'decision',
    },
    {
        'number': 6,
        'slug': 'build',
        'kind': 'Itinerary',
        'title': 'Build the Saturday',
        'blurb': 'Once voting closes, the best set of activities that fits the '
                 'budget and the hours is worked out for you.',
        'state': 'locked',
        'status': 'Opens when voting closes',
        'result': '',
        'meta': 'Jules closes voting · 2 votes outstanding',
        'cta': 'Preview the build',
        'route': 'build',
    },
]

# Things members have suggested, waiting on the organizer (FR-13, R-07).
PROPOSALS = {
    'pending': [
        {
            'name': 'Tram 28, end to end',
            'kind': 'Activity',
            'by': 'Leo',
            'when': 'Proposed 2 days ago',
            'meta': '€3 / person · €18 group · 1 hour',
            'blurb': 'The long way through Graça and Alfama, sitting down.',
        },
        {
            'name': 'A night out in Bairro Alto',
            'kind': 'Activity',
            'by': 'Theo',
            'when': 'Proposed yesterday',
            'meta': '€25 / person · €150 group · 3 hours',
            'blurb': 'Small bars, late, no plan beyond the first one.',
        },
    ],
    'decided': [
        {
            'name': 'Saturday sunset sail',
            'kind': 'Activity',
            'by': 'Nina',
            'state': 'approved',
            'note': 'In the vote',
        },
        {
            'name': 'Day trip to Sintra',
            'kind': 'Activity',
            'by': 'Maya',
            'state': 'rejected',
            'note': 'Needs a whole day; we only have the Saturday',
        },
        {
            'name': 'Seville',
            'kind': 'Destination',
            'by': 'Theo',
            'state': 'approved',
            'note': 'Was on the destination vote',
        },
    ],
}

# What the organizer can pin down before the itinerary is generated (FR-21).
CONSTRAINTS = {
    'must_have': [
        {'name': 'A wander through Alfama', 'meta': '€0 · 2 hours',
         'pinned': True},
        {'name': 'Saturday sunset sail', 'meta': '€35 / person · 2 hours',
         'pinned': True},
        {'name': 'Make your own azulejo', 'meta': '€30 / person · 2 hours',
         'pinned': False},
        {'name': 'A pastel de nata pit stop', 'meta': '€5 / person · 1 hour',
         'pinned': False},
    ],
    'day_budget': '120',
    'day_hours': 6,
    'hour_choices': [
        {'value': 4, 'label': '4 hours', 'note': 'Easy'},
        {'value': 6, 'label': '6 hours', 'note': 'Balanced'},
        {'value': 8, 'label': '8 hours', 'note': 'Full'},
    ],
}

# Closing the vote (FR-18, R-03, R-10).
CLOSE_VOTE = {
    'title': 'Close the vote on the Saturday?',
    'lede': 'Scores lock the moment you do. Nobody can add, change or remove '
            'one afterwards, and the itinerary is built from what is in now.',
    'voted': 4,
    'voters': 6,
    'outstanding': ['You', 'Nina'],
    'due': 'Fri, May 28 · 6 pm',
    'effects': [
        'The four activities keep the scores they have now.',
        'Two people will not have had a say on the Saturday.',
        'Nothing is booked or paid for — this only settles the plan.',
    ],
}

# The generated itinerary (FR-19, FR-20) with a reason per activity (FR-22).
BUILD = {
    'eyebrow': 'Saturday, Jun 19 · Lisbon',
    'title': 'Here’s the Saturday that fits.',
    'lede': 'The set of activities with the highest total group score that '
            'stays inside the budget and the hours. Nothing is confirmed '
            'until Jules approves it.',
    'meters': [
        {'label': 'Activity budget', 'value': '€240 of €360',
         'note': '€120 left in the shared activity budget', 'pct': 67},
        {'label': 'Hours planned', 'value': '5 of 6 hours',
         'note': '1 hour kept free', 'pct': 83},
    ],
    'score': {'label': 'Total group score', 'value': '13.50',
              'note': 'Across 3 activities · mean 4.50'},
    'included': [
        {'name': 'A wander through Alfama', 'time': '10:00', 'photo': 'alfama',
         'meta': '€0 total · 2 hours', 'score': '4.50',
         'reason': 'Pinned by the organizer, and the highest score at no cost.'},
        {'name': 'A pastel de nata pit stop', 'time': '12:30', 'photo': 'nata',
         'meta': '€30 total · 1 hour', 'score': '4.25',
         'reason': 'Cheapest hour on the list and nobody scored it below 3.'},
        {'name': 'Saturday sunset sail', 'time': '18:30', 'photo': 'sail',
         'meta': '€210 total · 2 hours', 'score': '4.75',
         'reason': 'Best score of the day; the €210 fits what is left.'},
    ],
    'excluded': [
        {'name': 'Make your own azulejo', 'photo': 'azulejo',
         'meta': '€180 total · 2 hours', 'score': '4.00',
         'reason': 'Adding it would need 7 hours, an hour more than the day '
                   'allows. Dropping the sail to fit it would cost 0.75 of '
                   'group score.'},
    ],
    'approve_note': 'Approving publishes the itinerary to everyone and lets a '
                    'read-only link be shared. You can still reorder it '
                    'afterwards.',
}


# Copy for the two proposal forms (FR-10, FR-11).
PROPOSE_FORMS = {
    'activity': {
        'kind': 'activity',
        'crumb': 'New activity',
        'eyebrow': 'Propose · Activity',
        'title': 'What should we make time for?',
        'submit': 'Send to the organizer',
        'durations': ['1 hour', '2 hours', '3 hours', 'Half a day'],
        'next_steps': [
            'Jules approves it, or says why not.',
            'Approved ideas join the Saturday vote.',
            'Everyone scores it 1 to 5.',
            'The build picks what fits the budget and the hours.',
        ],
    },
    'destination': {
        'kind': 'destination',
        'crumb': 'New destination',
        'eyebrow': 'Propose · Destination',
        'title': 'Somewhere you’d go back to.',
        'lede': 'Add a place to the vote. Everyone says yes or no, and the '
                'place with the most yeses is where the trip happens.',
        'submit': 'Add to the vote',
        'next_steps': [
            'Jules approves it, or says why not.',
            'It joins the destination vote.',
            'Everyone says yes or no.',
            'Most yeses wins; a tie is the organizer’s call.',
        ],
    },
}


# ---------------------------------------------------------------------------
# Joining from an invite link (FR-07), and the account steps it leans on
# (FR-01, FR-02). The link is a revocable token (NFR-02), so a dead link is a
# state this screen has to handle.

JOIN = {
    'token': '7f3b-91ac-24de',
    'inviter': {'name': 'Jules', 'initials': 'JU', 'role': 'organizer'},
    'already_in': 5,
    'facts': [
        {'icon': 'calendar', 'label': 'When', 'value': 'Jun 18–20, 2027',
         'note': '2 nights · Fri to Sun'},
        {'icon': 'wallet', 'label': 'Budget', 'value': '€2,700 shared',
         'note': 'One budget for the whole trip'},
        {'icon': 'users', 'label': 'Who', 'value': '5 friends so far',
         'note': 'You’d be the sixth'},
    ],
    'promise': 'Joining puts you in the group: you can propose places and '
               'activities, and your vote counts the same as everyone '
               'else’s.',
    'signup': {
        'title': 'Jules invited you to Lisbon.',
        'lede': 'Two nights in June, decided together. Make an account and '
                'you’re in.',
        'panel_title': 'Create your account',
        'submit': 'Join the trip',
        'alt_text': 'Already have an account?',
        'alt_link': 'Sign in instead',
    },
    'signin': {
        'title': 'Jules invited you to Lisbon.',
        'lede': 'Sign in and the trip is added to your list.',
        'panel_title': 'Sign in',
        'submit': 'Sign in & join',
        'alt_text': 'New here?',
        'alt_link': 'Create an account',
    },
    'expired': {
        'title': 'This link has expired.',
        'lede': 'Invite links can be replaced by the organizer, and the old '
                'one stops working the moment they make a new one. Nothing is '
                'wrong on your side.',
        'steps': [
            'Ask Jules for the current link.',
            'Or ask them to invite your email address directly.',
        ],
    },
    'welcome': {
        'eyebrow': 'You’re in',
        'title': 'Welcome to Lisbon.',
        'lede': 'Five friends were already here. Three things are waiting on '
                'you — no rush, but the first one closes on Friday.',
        'waiting': [
            {'title': 'Choose your stay',
             'note': '3 options · Due Fri, May 21', 'slug': 'stay',
             'icon': 'bed'},
            {'title': 'Score the Saturday',
             'note': '4 activities · Due Fri, May 28', 'slug': 'activities',
             'icon': 'clock'},
            {'title': 'Pick a way to the airport',
             'note': '3 options · Due Fri, Jun 4', 'slug': 'transfers',
             'icon': 'plane'},
        ],
        'cta': 'Go to the trip',
    },
}


# ---------------------------------------------------------------------------
# The read-only link (FR-09, FR-26, NFR-02).
#
# R-06 is the whole design here: a visitor sees the approved itinerary and
# nothing else. No names, no costs, no balances. The entries below
# are deliberately a different shape from ITINERARY - they carry no `meta`
# line, because that line is where the personal data lives.

SHARE = {
    'token': 'c41d-8f22-7b90',
    'link': 'tripsync.app/share/c41d-8f22-7b90',
    'created': 'Created by Vlad · Tue, Jun 1',
    'views': 'Opened 3 times',
    'title': 'Share the weekend, not the admin.',
    'lede': 'A read-only link for anyone who is not coming: parents, a '
            'flatmate, whoever is feeding the cat. They see the plan and '
            'nothing else.',
    'shown': [
        'The destination and the dates',
        'The agreed plans, by day, with times and places',
        'A drawn map of the Saturday stops and the route between them',
        'That there are six of you',
    ],
    'hidden': [
        'Where you are staying - it is not on the map or in the plans',
        'Everyone’s names and profiles',
        'What anything costs',
        'Who paid what, and who owes whom',
        'Votes, scores and anything still being decided',
    ],
    'revoke_note': 'Making a new link kills the old one immediately. Anyone '
                   'still holding it sees nothing.',
    'expired': {
        'title': 'This link is no longer active.',
        'lede': 'The group replaced or revoked it. Ask whoever sent it to you '
                'for the current one.',
    },
}

SHARED_ITINERARY = {
    'destination': 'Lisbon',
    'country': 'Portugal',
    'dates': 'Jun 18–20, 2027',
    'summary': 'A weekend for six.',
    'photo': 'lisbon',
    'days': [
        {
            'title': 'Friday, June 18',
            'note': 'Arriving',
            'entries': [
                {'time': '14:30', 'title': 'Hello, Lisbon',
                 'place': 'Santa Apolónia station', 'icon': 'train'},
                {'time': '19:30', 'title': 'First-night dinner',
                 'place': 'Taberna Sal Grosso · Alfama', 'icon': 'dinner'},
            ],
        },
        {
            'title': 'Saturday, June 19',
            'note': 'The full day',
            # the only day with a route worth drawing
            'map': True,
            'map_caption': 'The three stops above, in the order the day runs. '
                           'A sketch, not a navigation map.',
            'entries': [
                {'time': '10:00', 'title': 'A wander through Alfama',
                 'place': 'Starting at Miradouro de Santa Luzia',
                 'icon': 'pin'},
                {'time': '12:30', 'title': 'A pastel de nata pit stop',
                 'place': 'Manteigaria · Chiado', 'icon': 'coffee'},
                {'time': '18:30', 'title': 'Sunset on the water',
                 'place': 'Doca de Belém', 'icon': 'compass'},
            ],
        },
        {
            'title': 'Sunday, June 20',
            'note': 'Heading home',
            'entries': [
                {'time': '13:40', 'title': 'Leaving together',
                 'place': 'Rossio meeting point → Lisbon airport',
                 'icon': 'plane'},
            ],
        },
    ],
    'foot': 'Shared from Trip Sync. Read-only — nothing here can be '
            'changed, and nothing else is shared.',
}


# ---------------------------------------------------------------------------
# The map view of a day. Pin numbers match the drawn map in
# partials/map_lisbon.html; the stay is marked apart because it is where the
# day starts and ends, not a stop on the route.

ITINERARY_MAP = {
    'day': 'Saturday, June 19',
    'note': 'The agreed Saturday, on foot.',
    'base': {
        'name': 'Casa do Pátio',
        'meta': 'Graça · where everyone is staying',
        'label': 'Hotel',
    },
    'stops': [
        {
            'pin': 1, 'time': '10:00',
            'name': 'A wander through Alfama',
            'meta': 'Starting at Miradouro de Santa Luzia',
            'leg': '10 min walk downhill from the flat',
        },
        {
            'pin': 2, 'time': '12:30',
            'name': 'A pastel de nata pit stop',
            'meta': 'Manteigaria · Chiado',
            'leg': '20 min walk west, or tram 28 for two stops',
        },
        {
            'pin': 3, 'time': '18:30',
            'name': 'Sunset on the water',
            'meta': 'Doca de Belém',
            'leg': '25 min on the 15E tram along the river',
        },
    ],
    'back': 'Last tram back to Graça around 23:30.',
    'totals': [
        {'icon': 'compass', 'label': 'On foot', 'value': '3.4 km'},
        {'icon': 'clock', 'label': 'Moving between stops', 'value': '55 min'},
    ],
    'caveat': 'A sketch of the day, not a navigation map. Distances and '
              'times are rough.',
}


# ---------------------------------------------------------------------------
# Money (FR-27, FR-28, FR-29).
#
# One consistent set of numbers across the three screens. Five expenses,
# €945 spent of the €2,700 budget. Four are split across all six;
# the taxi is split between three, which is why "who it covers" is a field
# and not an assumption.
#
#   paid:   Jules 444  Theo 372  Nina 105  Maya 24  Vlad 0  Leo 0
#   share:  Vlad/Jules/Theo 153.50 each, Nina/Maya/Leo 161.50 each
#   so:     Jules +290.50  Theo +218.50  Nina -56.50  Maya -137.50
#           Vlad -153.50   Leo -161.50            (sums to zero)

MONEY = {
    'spent': '€945',
    'budget': '€2,700',
    'remaining': '€1,755 left',
    'spent_pct': 35,
    'your_share': '€153.50',
    'your_share_note': 'Your part of recorded expenses, calculated from the selected participants',
    'position': {
        'label': 'You owe',
        'amount': '€153.50',
        'note': 'One payment, to Jules.',
    },
    'paid_so_far': [
        {'name': 'Jules', 'initials': 'JU', 'amount': '€444'},
        {'name': 'Theo', 'initials': 'TH', 'amount': '€372'},
        {'name': 'Nina', 'initials': 'NI', 'amount': '€105'},
        {'name': 'Maya', 'initials': 'MA', 'amount': '€24'},
        {'name': 'Vlad', 'initials': 'VG', 'amount': '€0', 'is_me': True},
        {'name': 'Leo', 'initials': 'LE', 'amount': '€0'},
    ],
    'disclaimer': 'Trip Sync does not move money. It only keeps the sums '
                  'straight so nobody has to do it in a group chat.',
}

EXPENSES = [
    {
        'name': 'Casa do Pátio · deposit',
        'by': 'Jules', 'initials': 'JU',
        'date': 'Sat, May 22',
        'amount': '€444',
        'split': 'Split 6 ways · €74 each',
        'everyone': True,
        'icon': 'bed',
    },
    {
        'name': 'Return train tickets',
        'by': 'Theo', 'initials': 'TH',
        'date': 'Tue, May 25',
        'amount': '€312',
        'split': 'Split 6 ways · €52 each',
        'everyone': True,
        'icon': 'train',
    },
    {
        'name': 'Sunset sail · deposit',
        'by': 'Nina', 'initials': 'NI',
        'date': 'Tue, Jun 1',
        'amount': '€105',
        'split': 'Split 6 ways · €17.50 each',
        'everyone': True,
        'icon': 'compass',
    },
    {
        'name': 'Taberna Sal Grosso · deposit',
        'by': 'Theo', 'initials': 'TH',
        'date': 'Wed, Jun 2',
        'amount': '€60',
        'split': 'Split 6 ways · €10 each',
        'everyone': True,
        'icon': 'dinner',
    },
    {
        'name': 'Taxi from the station',
        'by': 'Maya', 'initials': 'MA',
        'date': 'Fri, Jun 18',
        'amount': '€24',
        'split': 'Maya, Leo, Nina · €8 each',
        'everyone': False,
        'icon': 'pin',
    },
]

BALANCES = {
    'owed': [
        {'name': 'Jules', 'initials': 'JU', 'amount': '€290.50',
         'note': 'Paid €444, share €153.50'},
        {'name': 'Theo', 'initials': 'TH', 'amount': '€218.50',
         'note': 'Paid €372, share €153.50'},
    ],
    'owes': [
        {'name': 'Leo', 'initials': 'LE', 'amount': '€161.50',
         'note': 'Paid nothing, share €161.50'},
        {'name': 'You', 'initials': 'VG', 'amount': '€153.50',
         'note': 'Paid nothing, share €153.50', 'is_me': True},
        {'name': 'Maya', 'initials': 'MA', 'amount': '€137.50',
         'note': 'Paid €24, share €161.50'},
        {'name': 'Nina', 'initials': 'NI', 'amount': '€56.50',
         'note': 'Paid €105, share €161.50'},
    ],
    'settle': [
        {'from': 'You', 'from_initials': 'VG', 'to': 'Jules',
         'to_initials': 'JU', 'amount': '€153.50', 'is_me': True},
        {'from': 'Leo', 'from_initials': 'LE', 'to': 'Jules',
         'to_initials': 'JU', 'amount': '€137.00', 'is_me': False},
        {'from': 'Leo', 'from_initials': 'LE', 'to': 'Theo',
         'to_initials': 'TH', 'amount': '€24.50', 'is_me': False},
        {'from': 'Maya', 'from_initials': 'MA', 'to': 'Theo',
         'to_initials': 'TH', 'amount': '€137.50', 'is_me': False},
        {'from': 'Nina', 'from_initials': 'NI', 'to': 'Theo',
         'to_initials': 'TH', 'amount': '€56.50', 'is_me': False},
    ],
    'settle_note': 'Five payments instead of the fifteen it would take if '
                   'everyone settled up with everyone.',
}

NEW_EXPENSE = {
    'title': 'What did you pay for?',
    'lede': 'Anything you covered for the group. It is split equally between '
            'whoever it was for, and the balances update straight away.',
    'payers': ['You', 'Jules', 'Theo', 'Nina', 'Maya', 'Leo'],
    'covers': [
        {'name': 'You', 'initials': 'VG', 'checked': True, 'is_me': True},
        {'name': 'Jules', 'initials': 'JU', 'checked': True},
        {'name': 'Theo', 'initials': 'TH', 'checked': True},
        {'name': 'Nina', 'initials': 'NI', 'checked': True},
        {'name': 'Maya', 'initials': 'MA', 'checked': True},
        {'name': 'Leo', 'initials': 'LE', 'checked': True},
    ],
    'derived': 'Six people · split equally',
    'submit': 'Record the expense',
}
