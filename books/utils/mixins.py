from rest_framework import viewsets


class ActionMixin(viewsets.ModelViewSet):
    action_serializers = {}

    def get_serializer_class(self):
        if (
            self.action_serializers
            and self.action in self.action_serializers
        ):
            return self.action_serializers[self.action]
        return super().get_serializer_class()
