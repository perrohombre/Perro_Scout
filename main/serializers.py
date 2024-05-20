# main/serializers.py
from rest_framework import serializers
from .models import Player, Club, League

class LeagueSerializer(serializers.ModelSerializer):
    class Meta:
        model = League
        fields = ['name']  # Zwracamy tylko nazwę ligi

class ClubSerializer(serializers.ModelSerializer):
    league = LeagueSerializer()  # Dodajemy serializer ligi

    class Meta:
        model = Club
        fields = ['name', 'league']  # Zwracamy nazwę klubu i ligę

class PlayerSerializer(serializers.ModelSerializer):
    club = ClubSerializer()  # Używamy serializera klubu, który zawiera ligę

    class Meta:
        model = Player
        fields = '__all__'
