import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.utils.exceptions import BotBlocked, ChatNotFound, UserDeactivated

from config import BOT_TOKEN, ADMIN_IDS, MESSAGES
from db import db
from sheets import sheets_manager
from keyboards import (
    get_contact_keyboard, 
    get_main_menu_keyboard,
    get_admin_menu_keyboard,
    get_projects_keyboard, 
    get_tasks_keyboard, 
    get_admin_keyboard,
    get_task_status_keyboard,
    get_add_note_keyboard
)
from utils.logger import logger

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN, parse_mode='HTML')
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Состояния FSM
class RegistrationStates(StatesGroup):
    waiting_for_contact = State()

class TaskSelectionStates(StatesGroup):
    selecting_project = State()
    selecting_task = State()

class NoteStates(StatesGroup):
    writing_note = State()

class LoggingMiddleware(BaseMiddleware):
    """Middleware для логирования всех событий (aiogram 2.x)."""

    async def on_pre_process_message(self, message: types.Message, data: dict):
        logger.info(f"Message from {message.from_user.id}: {message.text}")

    async def on_pre_process_callback_query(self, callback_query: types.CallbackQuery, data: dict):
        logger.info(f"Callback from {callback_query.from_user.id}: {callback_query.data}")

# Регистрация middleware
dp.middleware.setup(LoggingMiddleware())

# Обработчик ошибок
@dp.errors_handler()
async def errors_handler(update, exception):
    """Глобальный обработчик ошибок"""
    logger.error(f"Update {update} caused error {exception}")
    
    if isinstance(exception, (BotBlocked, ChatNotFound, UserDeactivated)):
        logger.warning(f"User blocked the bot or chat not found")
        return True
    
    return False

@dp.message_handler(commands=['start'], state='*')
async def start_command(message: types.Message, state: FSMContext):
    """Обработчик команды /start"""
    await state.finish()
    
    user_id = message.from_user.id
    user = await db.get_user(user_id)
    
    if user:
        is_admin = user_id in ADMIN_IDS
        keyboard = get_admin_menu_keyboard() if is_admin else get_main_menu_keyboard()
        
        await message.answer(
            MESSAGES['welcome_back'].format(name=user['name']),
            reply_markup=keyboard
        )
    else:
        await message.answer(
            MESSAGES['welcome_new'],
            reply_markup=get_contact_keyboard()
        )
        await RegistrationStates.waiting_for_contact.set()

@dp.message_handler(commands=['help'], state='*')
async def help_command(message: types.Message):
    """Обработчик команды /help"""
    help_text = (
        "<b>📖 Справка по боту</b>\n\n"
        "<b>Команды:</b>\n"
        "/start - Главное меню\n"
        "/help - Справка\n"
        "/cancel - Отменить текущее действие\n\n"
        "<b>Кнопки:</b>\n"
        "📋 Выбрать проект - Выбор проекта и задачи\n"
        "📝 Мои задачи - Просмотр ваших задач\n"
    )
    
    if message.from_user.id in ADMIN_IDS:
        help_text += (
            "\n<b>Админ-функции:</b>\n"
            "📊 Статистика - Статистика по боту\n"
            "📑 Все задачи - Просмотр всех задач\n"
        )
    
    await message.answer(help_text)

@dp.message_handler(commands=['cancel'], state='*')
async def cancel_command(message: types.Message, state: FSMContext):
    """Отмена текущего действия"""
    current_state = await state.get_state()
    
    if current_state is None:
        await message.answer("Нечего отменять.")
        return
    
    await state.finish()
    user = await db.get_user(message.from_user.id)
    
    if user:
        is_admin = message.from_user.id in ADMIN_IDS
        keyboard = get_admin_menu_keyboard() if is_admin else get_main_menu_keyboard()
        await message.answer("Действие отменено.", reply_markup=keyboard)
    else:
        await message.answer("Действие отменено.")

@dp.message_handler(content_types=['contact'], state=RegistrationStates.waiting_for_contact)
async def process_contact(message: types.Message, state: FSMContext):
    """Обработка отправленного контакта"""
    contact = message.contact
    user_id = message.from_user.id
    
    if contact.user_id != user_id:
        await message.answer(
            "❌ Пожалуйста, отправьте свой собственный контакт.",
            reply_markup=get_contact_keyboard()
        )
        return
    
    name = f"{contact.first_name} {contact.last_name or ''}".strip()
    phone = contact.phone_number
    
    success = await db.register_user(user_id, name, phone)
    
    if success:
        is_admin = user_id in ADMIN_IDS
        keyboard = get_admin_menu_keyboard() if is_admin else get_main_menu_keyboard()
        
        await message.answer(
            MESSAGES['registration_success'].format(name=name, phone=phone),
            reply_markup=keyboard
        )
        await state.finish()
    else:
        await message.answer(
            MESSAGES['registration_error'],
            reply_markup=get_contact_keyboard()
        )

@dp.message_handler(lambda message: message.text == "📋 Выбрать проект", state='*')
async def select_project(message: types.Message, state: FSMContext):
    """Обработчик выбора проекта"""
    await state.finish()
    
    user_id = message.from_user.id
    user = await db.get_user(user_id)
    
    if not user:
        await message.answer(MESSAGES['not_registered'])
        return
    
    projects = await sheets_manager.get_project_names()
    
    if not projects:
        await message.answer(MESSAGES['no_projects'])
        return
    
    await message.answer(
        "📋 Выберите проект:",
        reply_markup=get_projects_keyboard(projects)
    )
    await TaskSelectionStates.selecting_project.set()

@dp.message_handler(lambda message: message.text == "📝 Мои задачи", state='*')
async def my_tasks(message: types.Message, state: FSMContext):
    """Просмотр задач пользователя"""
    await state.finish()
    
    user_id = message.from_user.id
    user = await db.get_user(user_id)
    
    if not user:
        await message.answer(MESSAGES['not_registered'])
        return
    
    tasks = await db.get_user_tasks(user_id)
    
    if not tasks:
        await message.answer("У вас пока нет задач.")
        return
    
    response = "<b>📝 Ваши задачи:</b>\n\n"
    
    status_emoji = {
        'pending': '⏳',
        'approved': '✅',
        'rejected': '❌',
        'completed': '🎉'
    }
    
    for task in tasks:
        emoji = status_emoji.get(task['status'], '❓')
        response += (
            f"{emoji} <b>{task['project_name']}</b>\n"
            f"📝 {task['task_name']}\n"
            f"Статус: {task['status']}\n"
            f"Создано: {task['created_at'].strftime('%d.%m.%Y %H:%M')}\n\n"
        )
    
    await message.answer(response)


@dp.message_handler(lambda message: message.text == "✍️ Ввести данные", state='*')
async def start_write_data_from_main_menu(message: types.Message, state: FSMContext):
    """Запуск ввода комментария из главного меню на последнюю выбранную задачу пользователя."""
    await state.finish()

    user_id = message.from_user.id
    user = await db.get_user(user_id)
    if not user:
        await message.answer(MESSAGES['not_registered'])
        return

    # Берём последнюю ОДОБРЕННУЮ задачу
    tasks = await db.get_user_tasks(user_id, status='approved')
    if not tasks:
        await message.answer("У вас нет одобренных задач. Сначала дождитесь одобрения заявки.")
        return

    latest = tasks[0]
    project_name = latest['project_name']
    task_index = latest['task_index']

    await state.update_data(note_project=project_name, note_task_index=task_index)
    await NoteStates.writing_note.set()
    await message.answer(
        f"✍️ Отправьте текст для записи в столбец K\n"
        f"Проект: <b>{project_name}</b>, задача #{task_index + 1}",
        parse_mode='HTML'
    )

@dp.message_handler(lambda message: message.text == "📊 Статистика", state='*')
async def show_statistics(message: types.Message, state: FSMContext):
    """Показать статистику (только для админов)"""
    await state.finish()
    
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("❌ У вас нет доступа к этой функции.")
        return
    
    stats = await db.get_statistics()
    
    if not stats:
        await message.answer("❌ Не удалось получить статистику.")
        return
    
    response = (
        "<b>📊 Статистика бота</b>\n\n"
        f"👥 Всего пользователей: {stats.get('total_users', 0)}\n"
        f"✅ Активных (7 дней): {stats.get('active_users', 0)}\n\n"
        f"<b>Задачи:</b>\n"
        f"📋 Всего: {stats.get('total_tasks', 0)}\n"
        f"⏳ В ожидании: {stats.get('pending_tasks', 0)}\n"
        f"✅ Одобрено: {stats.get('approved_tasks', 0)}\n"
        f"❌ Отклонено: {stats.get('rejected_tasks', 0)}\n"
        f"🎉 Завершено: {stats.get('completed_tasks', 0)}\n"
    )
    
    if stats.get('top_projects'):
        response += "\n<b>Топ проектов:</b>\n"
        for project in stats['top_projects']:
            response += f"• {project['project_name']}: {project['count']}\n"
    
    await message.answer(response)

@dp.message_handler(lambda message: message.text == "📑 Все задачи", state='*')
async def all_tasks(message: types.Message, state: FSMContext):
    """Просмотр всех задач (только для админов)"""
    await state.finish()
    
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("❌ У вас нет доступа к этой функции.")
        return
    
    tasks = await db.get_all_tasks(limit=50)
    
    if not tasks:
        await message.answer("Задач пока нет.")
        return
    
    response = "<b>📑 Все задачи (последние 50):</b>\n\n"
    
    status_emoji = {
        'pending': '⏳',
        'approved': '✅',
        'rejected': '❌',
        'completed': '🎉'
    }
    
    for task in tasks[:20]:  # Показываем первые 20
        emoji = status_emoji.get(task['status'], '❓')
        response += (
            f"{emoji} <b>{task['name']}</b> ({task['phone']})\n"
            f"📋 {task['project_name']}\n"
            f"📝 {task['task_name'][:50]}...\n"
            f"Статус: {task['status']}\n\n"
        )
    
    if len(tasks) > 20:
        response += f"\n... и еще {len(tasks) - 20} задач"
    
    await message.answer(response)

@dp.callback_query_handler(lambda c: c.data.startswith('project_'), state=TaskSelectionStates.selecting_project)
async def process_project_selection(callback_query: types.CallbackQuery, state: FSMContext):
    """Обработка выбора проекта"""
    project_name = callback_query.data.replace('project_', '')
    await state.update_data(selected_project=project_name)
    
    tasks = await sheets_manager.get_tasks_from_project(project_name)
    
    if not tasks:
        await callback_query.message.edit_text(
            MESSAGES['no_tasks'].format(project=project_name)
        )
        await state.finish()
        return
    
    await callback_query.message.edit_text(
        f"📋 Проект: <b>{project_name}</b>\n\nВыберите задачу:",
        reply_markup=get_tasks_keyboard(tasks, project_name)
    )
    await TaskSelectionStates.selecting_task.set()

@dp.callback_query_handler(lambda c: c.data.startswith('task_'), state=TaskSelectionStates.selecting_task)
async def process_task_selection(callback_query: types.CallbackQuery, state: FSMContext):
    """Обработка выбора задачи"""
    parts = callback_query.data.split('_', 2)
    if len(parts) < 3:
        await callback_query.answer("❌ Ошибка в данных задачи")
        return
    
    project_name = parts[1]
    task_index = int(parts[2])
    
    user_id = callback_query.from_user.id
    user = await db.get_user(user_id)
    task_name = await sheets_manager.get_task_by_index(project_name, task_index)
    
    if not task_name:
        await callback_query.answer("❌ Задача не найдена")
        return
    
    task_id = await db.create_task_request(user_id, project_name, task_name, task_index)
    
    if not task_id:
        await callback_query.answer("❌ Ошибка при создании запроса")
        return
    
    await callback_query.message.edit_text(
        MESSAGES['request_sent'].format(project=project_name, task=task_name)
    )

    # Предлагаем пользователю добавить комментарий (будет записан в столбец K)
    try:
        await bot.send_message(
            user_id,
            "Хотите добавить комментарий к заявке? Это будет записано в столбец K выбранного проекта.",
            reply_markup=get_add_note_keyboard(project_name, task_index)
        )
    except Exception as e:
        logger.error(f"Error sending add-note prompt to user {user_id}: {e}")
    
    admin_message = MESSAGES['admin_new_request'].format(
        name=user['name'],
        phone=user['phone'],
        user_id=user_id,
        project=project_name,
        task=task_name
    )
    
    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(
                admin_id,
                admin_message,
                reply_markup=get_admin_keyboard(user_id, project_name, task_index)
            )
        except Exception as e:
            logger.error(f"Error sending message to admin {admin_id}: {e}")
    
    await state.finish()

@dp.callback_query_handler(lambda c: c.data == "back_to_projects", state=TaskSelectionStates.selecting_task)
async def back_to_projects(callback_query: types.CallbackQuery, state: FSMContext):
    """Возврат к выбору проектов"""
    projects = await sheets_manager.get_project_names()
    
    await callback_query.message.edit_text(
        "📋 Выберите проект:",
        reply_markup=get_projects_keyboard(projects)
    )
    await TaskSelectionStates.selecting_project.set()


@dp.callback_query_handler(lambda c: c.data.startswith('addnote_'), state='*')
async def start_add_note(callback_query: types.CallbackQuery, state: FSMContext):
    """Начинаем процесс добавления комментария пользователем (запись в K-столбец)."""
    try:
        parts = callback_query.data.split('_', 2)
        if len(parts) < 3:
            await callback_query.answer("❌ Ошибка данных")
            return
        project_name = parts[1]
        task_index = int(parts[2])

        # Разрешаем добавление комментария только для одобренных задач
        user_id = callback_query.from_user.id
        approved_tasks = await db.get_user_tasks(user_id, status='approved')
        is_approved = any(t['project_name'] == project_name and t['task_index'] == task_index for t in approved_tasks)

        if not is_approved:
            await callback_query.answer("Задача ещё не одобрена администратором")
            return

        await state.update_data(note_project=project_name, note_task_index=task_index)
        await NoteStates.writing_note.set()
        await callback_query.message.edit_text(
            f"✍️ Отправьте текст комментария для проекта <b>{project_name}</b>, задача #{task_index + 1}"
        )
    except Exception as e:
        logger.error(f"Error starting add note: {e}")
        await callback_query.answer("❌ Не удалось начать ввод комментария")


@dp.message_handler(state=NoteStates.writing_note, content_types=types.ContentTypes.TEXT)
async def receive_note_and_save(message: types.Message, state: FSMContext):
    """Получаем текст от пользователя и записываем в столбец K."""
    user_text = message.text.strip()
    if not user_text:
        await message.answer("Текст пустой. Пожалуйста, отправьте комментарий.")
        return

    data = await state.get_data()
    project_name = data.get('note_project')
    task_index = data.get('note_task_index')

    if project_name is None or task_index is None:
        await state.finish()
        await message.answer("❌ Не найден контекст задачи. Попробуйте заново через выбор задачи.")
        return

    # Проверяем, что задача одобрена
    approved_tasks = await db.get_user_tasks(message.from_user.id, status='approved')
    is_approved = any(t['project_name'] == project_name and t['task_index'] == int(task_index) for t in approved_tasks)

    if not is_approved:
        await state.finish()
        await message.answer("❌ Задача ещё не одобрена администратором. Комментарий можно добавить после одобрения.")
        return

    success = await sheets_manager.write_note_to_column_k(project_name, int(task_index), user_text)
    if success:
        await message.answer("✅ Комментарий сохранён в столбце K.")
    else:
        await message.answer("❌ Не удалось сохранить комментарий. Попробуйте позже.")

    await state.finish()

@dp.callback_query_handler(lambda c: c.data.startswith('approve_') or c.data.startswith('reject_'))
async def process_admin_decision(callback_query: types.CallbackQuery):
    """Обработка решения администратора"""
    if callback_query.from_user.id not in ADMIN_IDS:
        await callback_query.answer("❌ У вас нет прав администратора")
        return
    
    parts = callback_query.data.split('_')
    action = parts[0]
    user_id = int(parts[1])
    project_name = parts[2]
    task_index = int(parts[3])
    
    user = await db.get_user(user_id)
    task_name = await sheets_manager.get_task_by_index(project_name, task_index)
    
    if action == 'approve':
        await db.update_task_status(user_id, project_name, task_index, 'approved', callback_query.from_user.id)
        
        success = await sheets_manager.assign_task_to_user(
            project_name, task_index, user['name'], user['phone']
        )
        
        if success:
            await callback_query.message.edit_text(
                MESSAGES['admin_approved'].format(
                    name=user['name'],
                    phone=user['phone'],
                    project=project_name,
                    task=task_name
                )
            )
            
            try:
                await bot.send_message(
                    user_id,
                    MESSAGES['request_approved'].format(project=project_name, task=task_name)
                )
                # Предложим сразу добавить комментарий (запись в столбец K)
                await bot.send_message(
                    user_id,
                    "Можете добавить комментарий к задаче — он будет записан в столбец K.",
                    reply_markup=get_add_note_keyboard(project_name, task_index)
                )
            except Exception as e:
                logger.error(f"Error sending approval message to user {user_id}: {e}")
        else:
            await callback_query.answer("❌ Ошибка при записи в таблицу")
    
    else:
        await db.update_task_status(user_id, project_name, task_index, 'rejected', callback_query.from_user.id)
        
        await callback_query.message.edit_text(
            MESSAGES['admin_rejected'].format(
                name=user['name'],
                phone=user['phone'],
                project=project_name,
                task=task_name
            )
        )
        
        try:
            await bot.send_message(
                user_id,
                MESSAGES['request_rejected'].format(project=project_name, task=task_name)
            )
        except Exception as e:
            logger.error(f"Error sending rejection message to user {user_id}: {e}")

async def on_startup(dp):
    """Инициализация при запуске бота"""
    logger.info("Starting bot...")
    
    try:
        await db.create_pool()
        await sheets_manager.initialize()
        
        # Уведомляем админов о запуске
        for admin_id in ADMIN_IDS:
            try:
                await bot.send_message(admin_id, "🤖 Бот успешно запущен!")
            except:
                pass
        
        logger.info("Bot started successfully!")
    except Exception as e:
        logger.error(f"Error during startup: {e}")
        raise

async def on_shutdown(dp):
    """Очистка при остановке бота"""
    logger.info("Shutting down bot...")
    
    try:
        await db.close()
        
        # Уведомляем админов об остановке
        for admin_id in ADMIN_IDS:
            try:
                await bot.send_message(admin_id, "🤖 Бот остановлен.")
            except:
                pass
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")
    
    logger.info("Bot stopped")

if __name__ == '__main__':
    executor.start_polling(
        dp, 
        on_startup=on_startup, 
        on_shutdown=on_shutdown, 
        skip_updates=True,
        timeout=60
    )