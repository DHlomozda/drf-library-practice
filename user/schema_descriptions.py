from drf_spectacular.utils import extend_schema
from user.serializers import UserSerializer


create_user_schema = extend_schema(
    summary="Register a new user",
    description=(
        "Create a new user account.\n\n"
        "**Required fields:** email, first name, last name, password.\n"
        "- Password must be at least 6 characters long."
    ),
    request=UserSerializer,
    responses={201: UserSerializer},
)

manage_user_schema = extend_schema(
    summary="Get or update user profile",
    description=(
        "Authenticated users can retrieve or update their profile.\n"
        "- Only the current user's data is returned.\n"
        "- Updating password will automatically rehash it."
    ),
    request=UserSerializer,
    responses={200: UserSerializer},
)
