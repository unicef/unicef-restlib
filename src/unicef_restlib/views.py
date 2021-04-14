import functools
import operator

from django.db import ProgrammingError
from django.db.models import Q
from django.http import QueryDict
from rest_framework import exceptions


class MultiSerializerViewSetMixin:
    serializer_action_classes = {}

    def get_serializer_class(self):
        try:
            return self.serializer_action_classes[self.action]
        except (KeyError, AttributeError):
            return super().get_serializer_class()


class NestedViewSetMixin:
    """Allow viewsets inheritance with correct filtering depending on parents.
    """

    parent = None
    parent_lookup_kwarg = None
    parent_lookup_field = None

    @classmethod
    def _get_parents(cls):
        parents = []

        try:
            parent = cls.parent
            if parent:
                parents.append(parent)
                parents.extend(parent._get_parents())
        except AttributeError:
            pass

        return parents

    def get_parent_filter(self):
        return None

    def _get_parent_filters(self):
        parents = self._get_parents()

        filters = {}

        child = self
        lookups = []
        for parent in parents:
            lookups.append(child.parent_lookup_field)

            parent_filter = None
            if isinstance(child, NestedViewSetMixin):
                parent_filter = child.get_parent_filter()

            if parent_filter is None:
                parent_filter = {
                    '{}__{}'.format(
                        '__'.join(lookups), getattr(
                            child.parent,
                            'lookup_field',
                            'pk'
                        )
                    ): self.kwargs.get(child.parent_lookup_kwarg)
                }

            filters.update(parent_filter)
            child = parent

        return filters

    def get_parent(self):
        parent_class = getattr(self, 'parent', None)
        if not parent_class:
            return

        return parent_class(
            request=self.request,
            kwargs=self.kwargs,
            lookup_url_kwarg=self.parent_lookup_kwarg,
            action='parent',
        )

    def get_parent_object(self):
        # remove request query for a while to prevent incorrect filter
        # results for parent view
        query = self.request._request.GET
        self.request._request.GET = QueryDict()

        try:
            parent = self.get_parent()
            if not parent or not self.kwargs:
                return
            parent_object = parent.get_object()
        finally:
            self.request._request.GET = query

        return parent_object

    def get_root_object(self):
        # remove request query for a while to prevent incorrect filter
        # results for parent view
        query = self.request._request.GET
        self.request._request.GET = QueryDict()

        try:
            parents = self._get_parents()
            if not parents:
                return

            pre_root = parents[-2] if len(parents) > 1 else self
            root = parents[-1](
                request=self.request,
                kwargs=self.kwargs,
                lookup_url_kwarg=pre_root.parent_lookup_kwarg
            )

            root_object = root.get_object()
        finally:
            self.request._request.GET = query

        return root_object

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        queryset = queryset.filter(**self._get_parent_filters())
        return queryset


class SafeTenantViewSetMixin:
    def dispatch(self, request, *args, **kwargs):
        try:
            return super().dispatch(request, *args, **kwargs)
        except ProgrammingError:
            if request.user and not request.user.is_authenticated:
                raise exceptions.NotAuthenticated()
            raise


class QueryStringFilterMixin:
    """Mixin which allow to filter and search based on querystring filters"""
    search_param = 'search'
    filters = ()
    search_terms = ()

    def filter_params(self, filters=None):
        filters = filters or self.filters
        queries = []
        for param_filter, query_filter in filters:
            if param_filter in self.request.query_params:
                value = self.request.query_params.get(param_filter)
                if value in ["true", "false"]:
                    value = True if value == "true" else False
                or_queries = []
                if isinstance(query_filter, dict):
                    values = value.split(',')
                    for value in values:
                        filter_list = query_filter.get(value, [])
                        subqueries = [Q(**{dict_filter: dict_value}) for dict_filter, dict_value in filter_list]
                        or_queries.append(functools.reduce(operator.and_, subqueries))
                    queries.append(functools.reduce(operator.or_, or_queries))
                elif isinstance(query_filter, list):
                    subq = [Q(**{filter: value}) for filter in query_filter]
                    queries.append(functools.reduce(operator.or_, subq))
                else:
                    if query_filter.endswith('__in') and value:
                        value = value.split(',')
                    elif query_filter.endswith('__isnotnull'):
                        query_filter = query_filter.replace(
                            "__isnotnull",
                            "__isnull",
                        )
                        value = not value
                    queries.append(Q(**{query_filter: value}))
        return queries

    def search_params(self, search_terms=None):
        search_terms = search_terms or self.search_terms
        search_term = self.request.query_params.get(self.search_param)
        search_query = Q()
        if self.search_param in self.request.query_params:
            for param_filter in search_terms:
                q = Q(**{param_filter: search_term})
                search_query = search_query | q
        return search_query

    def get_queryset(self):
        qs = super().get_queryset()

        query_params = self.request.query_params
        if query_params:
            queries = []
            queries.extend(self.filter_params())
            queries.append(self.search_params())

            if queries:
                expression = functools.reduce(operator.and_, queries)
                qs = qs.filter(expression)
        return qs
