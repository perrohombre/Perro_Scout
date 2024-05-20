from rest_framework import generics
from .models import Player
from .serializers import PlayerSerializer

class PlayerList(generics.ListAPIView):
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer