from rest_framework import viewsets
from .models import Propiedad
from .serializers import PropiedadSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET'])
def check_admin(request):
    return Response({
        "isAdmin": request.user.is_staff
    })


class PropiedadViewSet(viewsets.ModelViewSet):
    queryset = Propiedad.objects.all()
    serializer_class = PropiedadSerializer