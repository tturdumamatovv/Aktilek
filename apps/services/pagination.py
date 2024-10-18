from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class CustomPagination(PageNumberPagination):
    page_size_query_param = 'page_size'  # Позволяет клиенту передавать page_size через запрос
    max_page_size = 100  # Устанавливаем максимальный размер страницы

    def get_paginated_response(self, data):
        # Проверяем, что self.page и self.page.paginator существуют
        if not self.page:
            return Response({
                'count': 0,
                'total_pages': 0,
                'next': None,
                'previous': None,
                'results': [],
            })

        return Response({
            'count': self.page.paginator.count if self.page.paginator else 0,
            'total_pages': self.page.paginator.num_pages if self.page.paginator else 0,  # Добавляем количество страниц
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data,
        })
