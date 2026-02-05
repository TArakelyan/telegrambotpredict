"""
Основной файл Telegram-бота для рассылки прогнозов Sports.ru
"""
import asyncio
import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)
import config
import handlers
from scheduler import PredictionScheduler

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def error_handler(update: object, context) -> None:
    """Обработчик ошибок"""
    logger.error(f"Exception while handling an update: {context.error}")


async def post_init(application: Application) -> None:
    """Действия после инициализации бота"""
    # Запускаем планировщик
    scheduler = PredictionScheduler(application.bot)
    scheduler.start()
    
    # Сохраняем планировщик в bot_data для доступа из других частей
    application.bot_data['scheduler'] = scheduler
    
    logger.info("✅ Бот запущен и готов к работе!")


async def post_shutdown(application: Application) -> None:
    """Действия при остановке бота"""
    # Останавливаем планировщик
    if 'scheduler' in application.bot_data:
        application.bot_data['scheduler'].stop()
    
    logger.info("🛑 Бот остановлен.")


def main():
    """Главная функция запуска бота"""
    logger.info("🔄 Инициализация бота...")
    
    # Создаем приложение
    application = (
        Application.builder()
        .token(config.BOT_TOKEN)
        .post_init(post_init)
        .post_shutdown(post_shutdown)
        .build()
    )
    
    # Регистрируем обработчики команд
    application.add_handler(CommandHandler("start", handlers.start_command))
    application.add_handler(CommandHandler("settings", handlers.settings_command))
    application.add_handler(CommandHandler("stop", handlers.stop_command))
    application.add_handler(CommandHandler("help", handlers.help_command))
    
    # Регистрируем обработчик callback-кнопок
    application.add_handler(CallbackQueryHandler(handlers.button_callback))
    
    # Регистрируем обработчик текстовых сообщений
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.text_message_handler))
    
    # Регистрируем обработчик ошибок
    application.add_error_handler(error_handler)
    
    # Всегда используем polling (надежнее для Render Free)
    logger.info("🚀 Запуск в режиме polling...")
    application.run_polling(
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True
    )


if __name__ == '__main__':
    main()
