from rest_framework_nested import routers


class NestedComplexRouter(routers.NestedSimpleRouter):
    """Set attributes for NestedViewSetMixin.
    Requires correct value for lookup argument,
    instead FieldError will be raised on queryset filtering.
    """

    def register(self, prefix, viewset, basename=None):
        super().register(prefix, viewset, basename=basename)

        # this is run in super()
        # re-running as we need that variables
        parent_registry = [
            registered for registered
            in self.parent_router.registry
            if registered[0] == self.parent_prefix
        ]
        parent_registry = parent_registry[0]
        parent_prefix, parent_viewset, parent_basename = parent_registry

        viewset.parent = parent_viewset
        viewset.parent_lookup_field = self.nest_prefix[:-1]
        viewset.parent_lookup_kwarg = self.nest_prefix + getattr(
            parent_viewset,
            'lookup_field',
            'pk'
        )
