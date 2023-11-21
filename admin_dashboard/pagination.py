from rest_framework.pagination import PageNumberPagination


class UserProfilePagination(PageNumberPagination):
    page_size = 2
    page_query_param = "q"
