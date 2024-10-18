from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class CustomPagination(PageNumberPagination):
    page_size = 10

    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,  # Добавляем количество страниц
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data,
        })
