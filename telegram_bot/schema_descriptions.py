from drf_spectacular.utils import extend_schema
from rest_framework.response import Response


go_to_bot_schema = extend_schema(
    summary="Get link to Telegram bot",
    description="Returns a direct link to the Telegram "
                "bot for the authenticated user.",
    responses={200: Response}
)
