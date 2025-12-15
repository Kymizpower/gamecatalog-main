from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from .models import Game


def index(request):
    """Главная страница с 8 последними играми"""
    games = Game.objects.filter(is_available=True).order_by('-created')[:8]
    return render(request, 'catalog/index.html', {'games': games})


def game_list(request):
    """Список всех игр с фильтрами, сортировкой и пагинацией"""
    # Получаем параметры фильтрации из GET-запроса
    genre = request.GET.get('genre', '')
    platform = request.GET.get('platform', '')
    sort_by = request.GET.get('sort', '-created')
    search_query = request.GET.get('search', '')
    price_min = request.GET.get('price_min', '')
    price_max = request.GET.get('price_max', '')
    available_only = request.GET.get('available', '')
    
    # Начинаем с всех игр
    games = Game.objects.all()
    
    # Фильтр по жанру
    if genre:
        games = games.filter(genre=genre)
    
    # Фильтр по платформе
    if platform:
        # Ищем игры, у которых в поле platform содержится выбранная платформа
        games = games.filter(platform__icontains=platform)
    
    # Фильтр по цене (от и до)
    if price_min:
        try:
            price_min_value = float(price_min)
            games = games.filter(price__gte=price_min_value)
        except ValueError:
            pass
    
    if price_max:
        try:
            price_max_value = float(price_max)
            games = games.filter(price__lte=price_max_value)
        except ValueError:
            pass
    
    # Фильтр по доступности
    if available_only:
        games = games.filter(is_available=True)
    
    # Поиск по названию или разработчику
    if search_query:
        games = games.filter(
            Q(title__icontains=search_query) | 
            Q(developer__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Сортировка
    sort_options = {
        'newest': '-created',           # Сначала новые
        'oldest': 'created',            # Сначала старые
        'price_asc': 'price',           # По цене (дешевые)
        'price_desc': '-price',         # По цене (дорогие)
        'name_asc': 'title',            # По названию (А-Я)
        'name_desc': '-title',          # По названию (Я-А)
        'rating_desc': '-metacritic_score',  # По рейтингу
    }
    
    if sort_by in sort_options:
        games = games.order_by(sort_options[sort_by])
    else:
        games = games.order_by('-created')  # По умолчанию новые сначала
    
    # Получаем общее количество отфильтрованных игр
    total_games = games.count()
    
    # ПАГИНАЦИЯ - 20 игр на страницу
    paginator = Paginator(games, 20)
    page = request.GET.get('page')
    
    try:
        games_paginated = paginator.page(page)
    except PageNotAnInteger:
        # Если страница не является целым числом, показываем первую страницу
        games_paginated = paginator.page(1)
    except EmptyPage:
        # Если страница выходит за пределы диапазона, показываем последнюю страницу
        games_paginated = paginator.page(paginator.num_pages)
    
    # Получаем уникальные жанры для фильтра
    all_genres = Game.objects.values_list('genre', flat=True).distinct()
    unique_genres = []
    seen = set()
    for genre_val in all_genres:
        if genre_val and genre_val not in seen:
            seen.add(genre_val)
            unique_genres.append(genre_val)
    
    # Получаем уникальные платформы
    all_platforms = []
    for game in Game.objects.all():
        if game.platform:
            # Разделяем платформы по запятой и добавляем в список
            platforms = [p.strip() for p in str(game.platform).split(',') if p.strip()]
            all_platforms.extend(platforms)
    unique_platforms = sorted(set(all_platforms))
    
    context = {
        'games': games_paginated,  # Используем пагинированные игры
        'genres': unique_genres,
        'platforms': unique_platforms,
        'selected_genre': genre,
        'selected_platform': platform,
        'selected_sort': sort_by,
        'search_query': search_query,
        'price_min': price_min,
        'price_max': price_max,
        'available_only': available_only,
        'total_games': total_games,
    }
    
    return render(request, 'catalog/game_list.html', context)


def game_detail(request, slug):
    """Детальная страница игры"""
    game = get_object_or_404(Game, slug=slug)
    
    # Похожие игры (по жанру)
    similar_games = Game.objects.filter(
        genre=game.genre
    ).exclude(
        id=game.id
    ).order_by('-created')[:4]
    
    context = {
        'game': game,
        'similar_games': similar_games,
    }

    return render(request, 'catalog/game_detail.html', context)


# О проекте
def about(request):
    """Страница 'О проекте'"""
    team_members = [
        {
            'name': 'Хуснутдинов Руслан',
            'description': 'Ответственный за вайб',
        },
        {
            'name': 'Хаджикулов Асадбек',
            'description': 'Ответсвенный за завозы',
        },
        {
            'name': 'Яскиев Магомед',
            'description': 'Ответсвенный за стиль по жизни',
        }
    ]
    
    tech_stack = [
        {'name': 'Django', 'icon': 'bi-gear', 'color': 'success', 'description': 'Веб-фреймворк для быстрой разработки'},
        {'name': 'SQLite', 'icon': 'bi-database', 'color': 'info', 'description': 'Легковесная база данных'},
        {'name': 'JavaScript', 'icon': 'bi-file-code', 'color': 'warning', 'description': 'Интерактивность и анимации'},
        {'name': 'Python', 'icon': 'bi-code-slash', 'color': 'primary', 'description': 'Основной язык программирования'},
        {'name': 'Pillow', 'icon': 'bi-image', 'color': 'danger', 'description': 'Обработка изображений'},
    ]
    
    context = {
        'team_members': team_members,
        'tech_stack': tech_stack,
        'page_title': 'О проекте GameCatalog',
        'page_description': 'Узнайте больше о нашей команде и технологиях, используемых в разработке GameCatalog.',
    }
    
    return render(request, 'catalog/about.html', context)
