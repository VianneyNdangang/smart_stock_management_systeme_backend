from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class CustomPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "limit"
    max_page_size = 100

    def paginate_queryset(self, queryset, request, view=None):
        self.view = view
        return super().paginate_queryset(queryset, request, view)

    def get_paginated_response(self, data):
        queryset = self.page.paginator.object_list

        summary = {}

        if hasattr(self, "view") and hasattr(self.view, "get_summary"):
            summary = self.view.get_summary(queryset)

        return Response({
            "items": data,
            "summary": summary,
            "page": self.page.number,
            "limit": self.page.paginator.per_page,
            "totalPages": self.page.paginator.num_pages,
            "total": self.page.paginator.count,
            "hasNext": self.page.has_next(),
            "hasPrev": self.page.has_previous(),
        })