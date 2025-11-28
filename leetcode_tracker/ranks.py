"""Rank system for LeetCode Tracker."""

from . import schemas


# Определение рангов с минимальным XP, иконкой и цветом
RANKS: list[dict[str, any]] = [
    {"name": "Beginner", "min_xp": 0, "icon": "🌱", "color": "#9ca3af"},
    {"name": "Apprentice", "min_xp": 100, "icon": "📝", "color": "#60a5fa"},
    {"name": "Skilled", "min_xp": 300, "icon": "⚔️", "color": "#34d399"},
    {"name": "Expert", "min_xp": 600, "icon": "🎯", "color": "#fbbf24"},
    {"name": "Master", "min_xp": 1000, "icon": "👑", "color": "#f97316"},
    {"name": "Grandmaster", "min_xp": 2000, "icon": "💎", "color": "#a855f7"},
    {"name": "Legend", "min_xp": 4000, "icon": "🔥", "color": "#ef4444"},
]


def get_rank_by_xp(xp: int) -> schemas.RankInfo:
    """
    Получить информацию о ранге по количеству XP.

    Args:
        xp: Количество XP пользователя

    Returns:
        RankInfo с информацией о ранге

    """
    current_rank = RANKS[0]

    for rank in RANKS:
        if xp >= rank["min_xp"]:
            current_rank = rank
        else:
            break

    return schemas.RankInfo(
        name=current_rank["name"], min_xp=current_rank["min_xp"], icon=current_rank["icon"], color=current_rank["color"]
    )


def get_all_ranks() -> list[schemas.RankInfo]:
    """
    Получить список всех рангов.

    Returns:
        Список всех доступных рангов

    """
    return [
        schemas.RankInfo(name=rank["name"], min_xp=rank["min_xp"], icon=rank["icon"], color=rank["color"])
        for rank in RANKS
    ]


def get_next_rank(current_xp: int) -> tuple[schemas.RankInfo | None, int]:
    """
    Получить информацию о следующем ранге и XP до него.

    Args:
        current_xp: Текущее количество XP

    Returns:
        Кортеж (следующий ранг или None, XP до следующего ранга)

    """
    for _i, rank in enumerate(RANKS):
        if current_xp < rank["min_xp"]:
            xp_needed = rank["min_xp"] - current_xp
            return (
                schemas.RankInfo(name=rank["name"], min_xp=rank["min_xp"], icon=rank["icon"], color=rank["color"]),
                xp_needed,
            )

    # Уже максимальный ранг
    return None, 0
