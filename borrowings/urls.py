from django.urls import path, include
from rest_framework import routers
from borrowings.views import (
    BorrowingViewSet,
    CreateBorrowingView,
)


router = routers.DefaultRouter()

router.register("borrowings", BorrowingViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("borrowings/create/", CreateBorrowingView.as_view(), name="create-borrowing"),
]

app_name = "borrowings"
