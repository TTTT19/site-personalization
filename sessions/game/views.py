from django.shortcuts import render


from .models import PlayerGameInfo, Player, Game


def show_home(request):
    context = {}
    request.session.modified = True
    request.session["player_id"] = request.session.session_key
    if request.method == 'POST' and 'number' in request.POST:
        request.session["game_id"] = request.POST['number']
        insert_data = Game(number=request.POST['number'], author=request.session["player_id"])
        insert_data.save()
    elif request.method == 'POST' and 'find_number' in request.POST:
        if 'attempts' not in request.session:
            request.session['attempts'] = 0
        request.session['attempts'] += 1
        hidden_number = Game.objects.filter(isActive=True).first()
        if int(request.POST['find_number']) > int(hidden_number.number):
            message = f"Загаданное число меньше числа{request.POST['find_number']}"
            context = {
                'message': message,

            }
        elif int(request.POST['find_number']) < int(hidden_number.number):
            message = f"Загаданное число больше числа {request.POST['find_number']}"
            context = {
                'message': message,

            }
        else:
            context = {
                'message': f'Вы угадали число с {request.session["attempts"]} попыток',

            }
            is_player_exist = Player.objects.filter(player=request.session["player_id"])
            if not is_player_exist:
                insert_finder_player = Player(player=request.session.session_key)
                insert_finder_player.save()
            insert_finished_data_game = PlayerGameInfo(player=Player.objects.get(player=request.session["player_id"]),
                                                       game=Game.objects.filter(number=hidden_number.number, isActive=True).first(),
                                                       attempt=request.session['attempts'])
            insert_finished_data_game.save()
            update_game = Game.objects.filter(isActive=True)
            update_game.update(isActive=False)
            request.session['attempts'] = 0
    else:
        active_game = Game.objects.filter(isActive=True)
        if not active_game:
            finished_game = PlayerGameInfo.objects.filter(game=Game.objects.filter(author=request.session["player_id"]).order_by('-id')[:1])
            context = {
                'active_game': False,
                'finished_game': finished_game,
            }
        else:
            for act_game in active_game:
                if request.session["player_id"] == act_game.author:
                    context = {
                        'game_id': act_game.number,
                        'attempt': "Ваше число ещё не угадали!"
                    }
                else:
                    context = {
                        'active_game': True,
                    }
    request.session.save()
    return render(
        request,
        'home.html',
        context
    )