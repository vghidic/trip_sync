from .db_context import user_context


def current_user(request):
    """The signed-in person, for the header avatar and greetings."""
    user = getattr(request, 'user', None)
    if user is None or not user.is_authenticated:
        return {}
    return {'user_profile': user_context(user)}
