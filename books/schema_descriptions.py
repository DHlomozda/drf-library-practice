from drf_spectacular.utils import extend_schema
from books.serializers import BookReadSerializer, BookCreateSerializer


book_list_schema = extend_schema(
    summary="Get list of books",
    description="Return a list of all books in the library.",
    responses={200: BookReadSerializer(many=True)},
)

book_retrieve_schema = extend_schema(
    summary="Retrieve a book",
    description="Get detailed information about a specific book by its ID.",
    responses={200: BookReadSerializer},
)

book_create_schema = extend_schema(
    summary="Create a book",
    description=(
        "Admins only. Create a new book in the system.\n\n"
        "Validation rules:\n"
        "- **inventory** must be a positive integer\n"
        "- **daily_fee** must be a positive number\n"
        "- Combination of **title** and **author** must be unique\n"
        "- **cover** must be either HARD or SOFT"
    ),
    request=BookCreateSerializer,
    responses={201: BookCreateSerializer},
)

book_update_schema = extend_schema(
    summary="Update a book",
    description=(
        "Admins only. Fully update an existing book.\n\n"
        "Same validation rules as for creation."
    ),
    request=BookCreateSerializer,
    responses={200: BookCreateSerializer},
)

book_partial_update_schema = extend_schema(
    summary="Partially update a book",
    description=(
        "Admins only. Update one or more fields of an existing book.\n\n"
        "Same validation rules as for creation."
    ),
    request=BookCreateSerializer,
    responses={200: BookCreateSerializer},
)

book_destroy_schema = extend_schema(
    summary="Delete a book",
    description="Admins only. Permanently delete a book by its ID.",
    responses={204: None},
)
