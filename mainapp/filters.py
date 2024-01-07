from rest_framework import filters


class UserFilterBackend(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        if request.user.is_superuser:
            return queryset
        else:
            return queryset.filter(user=request.user.client)