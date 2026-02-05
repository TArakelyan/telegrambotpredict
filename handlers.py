"""
Обработчики команд и callback'ов бота
"""
from telegram import Update
from telegram.ext import ContextTypes
from database import Database
import keyboards
import config


db = Database()


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    user = update.effective_user
    
    # Добавляем пользователя в БД
    db.add_user(
        user_id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name
    )
    
    # Проверяем, есть ли у пользователя уже подписки
    user_sports = db.get_user_sports(user.id)
    
    if user_sports:
        await update.message.reply_text(
            f"Привет, {user.first_name}! 👋\n\n"
            f"Ты уже подписан на прогнозы Sports.ru.\n\n"
            f"Используй /settings для изменения настроек.",
            reply_markup=keyboards.get_main_menu_keyboard()
        )
    else:
        await update.message.reply_text(
            f"Привет, {user.first_name}! 👋\n\n"
            f"Я буду присылать тебе прогнозы с Sports.ru.\n\n"
            f"Выбери виды спорта, которые тебя интересуют:",
            reply_markup=keyboards.get_sports_keyboard()
        )


async def settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /settings"""
    user = update.effective_user
    user_sports = db.get_user_sports(user.id)
    
    if not user_sports:
        await update.message.reply_text(
            "У тебя пока нет подписок. Выбери виды спорта:",
            reply_markup=keyboards.get_sports_keyboard()
        )
        return
    
    sports_list = [config.SPORTS.get(sport, sport) for sport in user_sports]
    
    await update.message.reply_text(
        f"Твои текущие подписки:\n\n" + "\n".join([f"• {sport}" for sport in sports_list]) + "\n\n"
        f"Что хочешь изменить?",
        reply_markup=keyboards.get_settings_keyboard()
    )


async def stop_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /stop"""
    user = update.effective_user
    
    await update.message.reply_text(
        "Ты уверен, что хочешь отключить все уведомления?",
        reply_markup=keyboards.get_confirmation_keyboard("stop")
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /help"""
    help_text = (
        "📖 <b>Помощь по командам</b>\n\n"
        "/start - Начать работу с ботом\n"
        "/settings - Настроить подписки\n"
        "/stop - Отключить уведомления\n"
        "/help - Показать эту справку\n\n"
        "<b>Как это работает:</b>\n"
        "1. Выбери виды спорта, которые тебя интересуют\n"
        "2. Опционально выбери конкретные турниры\n"
        "3. Получай прогнозы автоматически!\n\n"
        "Каждый прогноз содержит краткое описание и ссылку для ставки."
    )
    
    await update.message.reply_text(help_text, parse_mode='HTML')


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик нажатий на inline-кнопки"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    data = query.data
    
    # Выбор вида спорта
    if data.startswith("sport_"):
        sport = data.replace("sport_", "")
        user_sports = db.get_user_sports(user_id)
        
        if sport in user_sports:
            db.remove_user_sport(user_id, sport)
        else:
            db.add_user_sport(user_id, sport)
        
        updated_sports = db.get_user_sports(user_id)
        await query.edit_message_text(
            "Выбери виды спорта, которые тебя интересуют:",
            reply_markup=keyboards.get_sports_keyboard(updated_sports)
        )
    
    # Завершение выбора видов спорта
    elif data == "sports_done":
        user_sports = db.get_user_sports(user_id)
        
        if not user_sports:
            await query.edit_message_text(
                "Выбери хотя бы один вид спорта!",
                reply_markup=keyboards.get_sports_keyboard()
            )
            return
        
        await query.edit_message_text(
            "Отлично! Хочешь настроить фильтр по турнирам?\n\n"
            "Если нет, ты будешь получать все прогнозы по выбранным видам спорта.",
            reply_markup=keyboards.get_sport_selection_for_tournaments_keyboard(user_sports)
        )
    
    # Настройка турниров для конкретного вида спорта
    elif data.startswith("configure_tournaments_"):
        sport = data.replace("configure_tournaments_", "")
        user_tournaments = db.get_user_tournaments(user_id, sport)
        
        await query.edit_message_text(
            f"Выбери турниры {config.SPORTS.get(sport, sport)}, которые тебя интересуют:\n\n"
            f"Если не выберешь ни одного - будут приходить все прогнозы.",
            reply_markup=keyboards.get_tournaments_keyboard(sport, user_tournaments)
        )
    
    # Выбор турнира
    elif data.startswith("tournament_"):
        parts = data.replace("tournament_", "").split("_", 1)
        if len(parts) == 2:
            sport, tournament = parts
            user_tournaments = db.get_user_tournaments(user_id, sport)
            
            if tournament in user_tournaments:
                db.remove_user_tournament(user_id, sport, tournament)
            else:
                db.add_user_tournament(user_id, sport, tournament)
            
            updated_tournaments = db.get_user_tournaments(user_id, sport)
            await query.edit_message_text(
                f"Выбери турниры {config.SPORTS.get(sport, sport)}, которые тебя интересуют:\n\n"
                f"Если не выберешь ни одного - будут приходить все прогнозы.",
                reply_markup=keyboards.get_tournaments_keyboard(sport, updated_tournaments)
            )
    
    # Завершение выбора турниров
    elif data.startswith("tournaments_done_"):
        sport = data.replace("tournaments_done_", "")
        user_sports = db.get_user_sports(user_id)
        
        await query.edit_message_text(
            "Настройки сохранены! ✅\n\n"
            "Теперь ты будешь получать прогнозы согласно своим предпочтениям.",
            reply_markup=keyboards.get_sport_selection_for_tournaments_keyboard(user_sports)
        )
    
    # Возврат к выбору видов спорта
    elif data == "back_to_sports":
        user_sports = db.get_user_sports(user_id)
        await query.edit_message_text(
            "Выбери виды спорта, которые тебя интересуют:",
            reply_markup=keyboards.get_sports_keyboard(user_sports)
        )
    
    # Возврат к настройкам
    elif data == "back_to_settings":
        user_sports = db.get_user_sports(user_id)
        sports_list = [config.SPORTS.get(sport, sport) for sport in user_sports]
        
        await query.edit_message_text(
            f"Твои текущие подписки:\n\n" + "\n".join([f"• {sport}" for sport in sports_list]) + "\n\n"
            f"Что хочешь изменить?",
            reply_markup=keyboards.get_settings_keyboard()
        )
    
    # Изменение видов спорта из настроек
    elif data == "change_sports":
        user_sports = db.get_user_sports(user_id)
        await query.edit_message_text(
            "Выбери виды спорта, которые тебя интересуют:",
            reply_markup=keyboards.get_sports_keyboard(user_sports)
        )
    
    # Настройка турниров из настроек
    elif data == "change_tournaments":
        user_sports = db.get_user_sports(user_id)
        
        if not user_sports:
            await query.edit_message_text(
                "Сначала выбери виды спорта!",
                reply_markup=keyboards.get_sports_keyboard()
            )
            return
        
        await query.edit_message_text(
            "Выбери вид спорта для настройки турниров:",
            reply_markup=keyboards.get_sport_selection_for_tournaments_keyboard(user_sports)
        )
    
    # Очистка всех подписок
    elif data == "clear_all":
        await query.edit_message_text(
            "Ты уверен, что хочешь очистить все подписки?",
            reply_markup=keyboards.get_confirmation_keyboard("clear_all")
        )
    
    # Подтверждение действий
    elif data.startswith("confirm_"):
        action = data.replace("confirm_", "")
        
        if action == "stop":
            db.update_user_status(user_id, False)
            await query.edit_message_text(
                "Уведомления отключены. ❌\n\n"
                "Используй /start, чтобы снова включить их."
            )
        
        elif action == "clear_all":
            db.clear_user_sports(user_id)
            await query.edit_message_text(
                "Все подписки очищены. 🗑\n\n"
                "Используй /start, чтобы настроить заново."
            )
    
    # Отмена действий
    elif data.startswith("cancel_"):
        await query.edit_message_text("Действие отменено.")


async def text_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик текстовых сообщений"""
    text = update.message.text
    
    if text == "⚙️ Настройки подписок":
        await settings_command(update, context)
    
    elif text == "ℹ️ Информация":
        await help_command(update, context)
    
    elif text == "🛑 Отключить уведомления":
        await stop_command(update, context)
    
    else:
        await update.message.reply_text(
            "Используй меню ниже для управления ботом или /help для справки.",
            reply_markup=keyboards.get_main_menu_keyboard()
        )
