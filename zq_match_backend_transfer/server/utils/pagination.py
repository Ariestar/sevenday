"""
自定义分页器
"""
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class StandardResultsSetPagination(PageNumberPagination):
    """标准分页器"""
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100
    
    def get_paginated_response(self, data):
        return Response({
            'code': '00000',
            'msg': '',
            'data': {
                'count': self.page.paginator.count,
                'next': self.get_next_link(),
                'previous': self.get_previous_link(),
                'results': data,
                'page': self.page.number,
                'page_size': self.get_page_size(self.request),
                'total_pages': self.page.paginator.num_pages,
            }
        })


class LargeResultsSetPagination(PageNumberPagination):
    """大数据集分页器"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 200


class SmallResultsSetPagination(PageNumberPagination):
    """小数据集分页器"""
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 50
