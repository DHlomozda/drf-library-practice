from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
import os

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def go_to_bot(request):
    telegram_bot_username = os.getenv("TELEGRAM_BOT_USERNAME", "BorrowingBookBot")
    return Response({"bot_link": f"https://t.me/BorrowingBookBot"})