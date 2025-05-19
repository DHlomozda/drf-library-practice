from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from borrowings.models import Borrowing
from borrowings.serializers import BorrowingReadSerializer


class BorrowingViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Borrowing.objects.select_related("book", "user")
    serializer_class = BorrowingReadSerializer


class CreateBorrowingView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs) -> Response:
        serializer = BorrowingReadSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
