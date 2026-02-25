from rest_framework.permissions import BasePermission


class IsFarmOwner(BasePermission):
    """
    Allows access only to owners of the farm
    associated with the cattle object.
    """

    def has_object_permission(self, request, view, obj):
        # obj here is a Cattle instance
        return obj.farm.owner == request.user
