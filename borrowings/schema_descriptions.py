from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from borrowings.serializers import (
    BorrowingReadSerializer,
    BorrowingCreateSerializer,
)


borrowing_list_schema = extend_schema(
    summary="Get list of borrowings",
    description=(
        "Get a list of borrowings.\n\n"
        "Authentication required: Yes\n"
        "Permissions:\n"
        "- Admins can view all borrowings\n"
        "- Regular users can only view their own borrowings\n\n"
        "Filtering:\n"
        "- Admins can filter by user_id\n"
        "- All users can filter by is_active status"
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
            description="Filter borrowings by active "
                        "status (true = not returned)",
        ),
    ],
    responses={
        200: BorrowingReadSerializer(many=True),
        401: OpenApiTypes.OBJECT
    },
)

borrowing_retrieve_schema = extend_schema(
    summary="Retrieve a borrowing",
    description=(
        "Get detailed information about a specific borrowing.\n\n"
        "Authentication required: Yes\n"
        "Permissions:\n"
        "- Admins can view any borrowing\n"
        "- Regular users can only view their own borrowings"
    ),
    responses={
        200: BorrowingReadSerializer,
        401: OpenApiTypes.OBJECT,
        403: OpenApiTypes.OBJECT,
        404: OpenApiTypes.OBJECT
    },
)

borrowing_create_schema = extend_schema(
    summary="Create a borrowing",
    description=(
        "Create a new borrowing and initialize Stripe payment session.\n\n"
        "Authentication required: Yes\n"
        "Permissions:\n"
        "- Only authenticated users can create borrowings\n\n"
        "Validation rules:\n"
        "- User cannot have any pending or expired payments\n"
        "- Book must be available in inventory\n"
        "- Expected return date must be in the future\n"
        "- User must be authenticated"
    ),
    request=BorrowingCreateSerializer,
    responses={
        201: BorrowingCreateSerializer,
        400: OpenApiTypes.OBJECT,
        401: OpenApiTypes.OBJECT
    },
)

borrowing_update_schema = extend_schema(
    summary="Update a borrowing",
    description=(
        "Fully update an existing borrowing.\n\n"
        "Authentication required: Yes\n"
        "Permissions:\n"
        "- Admins can update any borrowing\n"
        "- Regular users can only update their own borrowings"
    ),
    request=BorrowingCreateSerializer,
    responses={
        200: BorrowingCreateSerializer,
        401: OpenApiTypes.OBJECT,
        403: OpenApiTypes.OBJECT,
        404: OpenApiTypes.OBJECT
    },
)

borrowing_partial_update_schema = extend_schema(
    summary="Partially update a borrowing",
    description=(
        "Update selected fields of a borrowing.\n\n"
        "Authentication required: Yes\n"
        "Permissions:\n"
        "- Admins can update any borrowing\n"
        "- Regular users can only update their own borrowings"
    ),
    request=BorrowingCreateSerializer,
    responses={
        200: BorrowingCreateSerializer,
        401: OpenApiTypes.OBJECT,
        403: OpenApiTypes.OBJECT,
        404: OpenApiTypes.OBJECT
    },
)

borrowing_destroy_schema = extend_schema(
    summary="Delete a borrowing",
    description=(
        "Delete a borrowing by ID.\n\n"
        "Authentication required: Yes\n"
        "Permissions:\n"
        "- Only admins can delete borrowings"
    ),
    responses={
        204: None,
        401: OpenApiTypes.OBJECT,
        403: OpenApiTypes.OBJECT,
        404: OpenApiTypes.OBJECT
    },
)

borrowing_return_schema = extend_schema(
    summary="Return a book",
    description=(
        "Mark the borrowing as returned and increase book inventory.\n\n"
        "Authentication required: Yes\n"
        "Permissions:\n"
        "- Admins can return any book\n"
        "- Regular users can only return their own books\n\n"
        "Note: If the book is returned late, "
        "a fine will be automatically calculated "
        "and a payment session will be created."
    ),
    responses={
        200: OpenApiTypes.OBJECT,
        400: OpenApiTypes.OBJECT,
        401: OpenApiTypes.OBJECT,
        403: OpenApiTypes.OBJECT,
        404: OpenApiTypes.OBJECT
    },
)
