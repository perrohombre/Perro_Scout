from django.shortcuts import render
from django.http import HttpResponse
from .models import Player

def player_list(request):
    players = Player.objects.all()
    return render(request, 'player_list.html', {'players': players})

def test_db_connection(request):
    try:
        players = Player.objects.all()
        if players.exists():
            return HttpResponse(f"Found {players.count()} players in the database.")
        else:
            return HttpResponse("No players found in the database.")
    except Exception as e:
        return HttpResponse(f"Error: {str(e)}")