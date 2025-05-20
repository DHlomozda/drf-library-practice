from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from borrowings.serializers import (
    BorrowingReadSerializer,
    BorrowingCreateSerializer,
)


borrowing_list_schema = extend_schema(
    summary="Get list of borrowings",
    description=(
        "Admins can view all borrowings and filter by user ID or active status.\n"
        "Regular users see only their own borrowings."
    ),
    parameters=[
        OpenApiParameter(
            name="user_id",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description="Filter by user ID (admin only)",
        ),
        OpenApiParameter(
            name="is_active",
            type=OpenApiTypes.BOOL,
            location=OpenApiParameter.QUERY,
            description="Filter borrowings by active status (true = not returned)",
        ),
    ],
    responses={200: BorrowingReadSerializer(many=True)},
)

borrowing_retrieve_schema = extend_schema(
    summary="Retrieve a borrowing",
    description="Get detailed information about a specific borrowing.",
    responses={200: BorrowingReadSerializer},
)

borrowing_create_schema = extend_schema(
    summary="Create a borrowing",
    description="Create a new borrowing and initialize Stripe payment session.",
    request=BorrowingCreateSerializer,
    responses={201: BorrowingCreateSerializer},
)

borrowing_update_schema = extend_schema(
    summary="Update a borrowing",
    description="Fully update an existing borrowing.",
    request=BorrowingCreateSerializer,
    responses={200: BorrowingCreateSerializer},
)

borrowing_partial_update_schema = extend_schema(
    summary="Partially update a borrowing",
    description="Update selected fields of a borrowing.",
    request=BorrowingCreateSerializer,
    responses={200: BorrowingCreateSerializer},
)

borrowing_destroy_schema = extend_schema(
    summary="Delete a borrowing",
    description="Delete a borrowing by ID (admin only).",
    responses={204: None},
)

borrowing_return_schema = extend_schema(
    summary="Return a book",
    description="Mark the borrowing as returned and increase book inventory.",
    responses={200: None},
)
