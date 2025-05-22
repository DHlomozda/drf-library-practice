from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
import os

from telegram_bot.schema_descriptions import go_to_bot_schema


@go_to_bot_schema
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def go_to_bot(request):
    telegram_bot_username = os.getenv(
        "TELEGRAM_BOT_USERNAME",
        "BorrowingBookBot"
    )  # TO-DO 'telegram_bot_username' is assigned to but never used
    return Response({"bot_link": "https://t.me/BorrowingBookBot"})
