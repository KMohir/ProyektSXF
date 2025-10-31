from aiogram import types
from typing import List


def get_contact_keyboard() -> types.ReplyKeyboardMarkup:
    """Клавиатура с кнопкой отправки контакта."""
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(types.KeyboardButton(text="📱 Отправить контакт", request_contact=True))
    return keyboard


def get_main_menu_keyboard() -> types.ReplyKeyboardMarkup:
    """Главное меню для обычного пользователя."""
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row(
        types.KeyboardButton(text="📋 Выбрать проект"),
        types.KeyboardButton(text="📝 Мои задачи"),
    )
    keyboard.add(types.KeyboardButton(text="✍️ Ввести данные"))
    return keyboard


def get_admin_menu_keyboard() -> types.ReplyKeyboardMarkup:
    """Главное меню для администратора (доп. кнопки)."""
    keyboard = get_main_menu_keyboard()
    keyboard.row(
        types.KeyboardButton(text="📊 Статистика"),
        types.KeyboardButton(text="📑 Все задачи"),
    )
    return keyboard


def get_projects_keyboard(projects: List[str]) -> types.InlineKeyboardMarkup:
    """Инлайн-клавиатура со списком проектов."""
    markup = types.InlineKeyboardMarkup()
    for name in projects:
        markup.add(
            types.InlineKeyboardButton(text=name, callback_data=f"project_{name}")
        )
    return markup


def get_tasks_keyboard(tasks: List[str], project_name: str) -> types.InlineKeyboardMarkup:
    """Инлайн-клавиатура со списком задач для выбранного проекта."""
    markup = types.InlineKeyboardMarkup()
    for idx, task in enumerate(tasks):
        # Ограничим длину названия кнопки, чтобы не разъезжалась разметка
        title = task if len(task) <= 64 else task[:61] + "..."
        markup.add(
            types.InlineKeyboardButton(
                text=title,
                callback_data=f"task_{project_name}_{idx}",
            )
        )
    # Кнопка "Назад к проектам"
    markup.add(
        types.InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_projects")
    )
    return markup


def get_admin_keyboard(user_id: int, project_name: str, task_index: int) -> types.InlineKeyboardMarkup:
    """Инлайн-клавиатура для админа: Одобрить / Отклонить."""
    markup = types.InlineKeyboardMarkup()
    approve_cb = f"approve_{user_id}_{project_name}_{task_index}"
    reject_cb = f"reject_{user_id}_{project_name}_{task_index}"
    markup.row(
        types.InlineKeyboardButton(text="✅ Одобрить", callback_data=approve_cb),
        types.InlineKeyboardButton(text="❌ Отклонить", callback_data=reject_cb),
    )
    return markup


def get_task_status_keyboard() -> types.InlineKeyboardMarkup:
    """Заготовка клавиатуры статуса задачи (на будущее)."""
    # В текущей логике не используется, но импортируется в bot.py.
    return types.InlineKeyboardMarkup()


def get_add_note_keyboard(project_name: str, task_index: int) -> types.InlineKeyboardMarkup:
    """Инлайн-клавиатура для добавления комментария пользователем (запись в столбец K)."""
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton(
            text="✍️ Добавить комментарий",
            callback_data=f"addnote_{project_name}_{task_index}",
        )
    )
    return markup


