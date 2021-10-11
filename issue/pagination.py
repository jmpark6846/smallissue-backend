from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class DefaultPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_num'

    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,
            'list': data,
            'page_size': self.page_size,
            'current_page': self.page.number
        })