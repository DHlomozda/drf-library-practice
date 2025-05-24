from django.urls import path
from telegram_bot import views

app_name = "telegram_bot"
urlpatterns = [
    path("go-to-bot/", views.go_to_bot, name="go-to-bot"),
]
