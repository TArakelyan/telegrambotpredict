"""
Планировщик задач для проверки новых прогнозов
"""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from telegram import Bot
from database import Database
from parser import PredictionsParser
import keyboards
import config
import asyncio


class PredictionScheduler:
    def __init__(self, bot: Bot):
        self.bot = bot
        self.db = Database()
        self.parser = PredictionsParser()
        self.scheduler = AsyncIOScheduler()
        
    def start(self):
        """Запустить планировщик"""
        # Проверка новых прогнозов каждые N секунд
        self.scheduler.add_job(
            self.check_new_predictions,
            'interval',
            seconds=config.CHECK_INTERVAL,
            id='check_predictions'
        )
        
        self.scheduler.start()
        print(f"✅ Планировщик запущен. Интервал проверки: {config.CHECK_INTERVAL} сек.")
    
    async def check_new_predictions(self):
        """Проверить новые прогнозы и разослать их"""
        try:
            print("🔍 Проверяю новые прогнозы...")
            
            # Получаем URLs уже отправленных прогнозов
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT prediction_url FROM sent_predictions')
            sent_urls = {row['prediction_url'] for row in cursor.fetchall()}
            conn.close()
            
            # Получаем новые прогнозы
            new_predictions = self.parser.get_new_predictions(sent_urls)
            
            if not new_predictions:
                print("ℹ️ Новых прогнозов нет.")
                return
            
            print(f"✨ Найдено новых прогнозов: {len(new_predictions)}")
            
            # Отправляем каждый прогноз подходящим пользователям
            for prediction in new_predictions:
                await self.send_prediction_to_users(prediction)
                
                # Добавляем задержку между отправками
                await asyncio.sleep(1)
            
            print("✅ Рассылка завершена.")
            
        except Exception as e:
            print(f"❌ Ошибка при проверке прогнозов: {e}")
    
    async def send_prediction_to_users(self, prediction: dict):
        """Отправить прогноз подходящим пользователям"""
        try:
            # Получаем список пользователей для этого прогноза
            users = self.db.get_users_for_prediction(
                prediction['sport'],
                prediction['tournament']
            )
            
            if not users:
                print(f"ℹ️ Нет подписчиков для прогноза: {prediction['title']}")
                return
            
            # Формируем сообщение
            message = self._format_prediction_message(prediction)
            
            # Отправляем каждому пользователю
            sent_count = 0
            for user_id in users:
                try:
                    await self.bot.send_message(
                        chat_id=user_id,
                        text=message,
                        parse_mode='HTML',
                        reply_markup=keyboards.get_partner_button(prediction['partner_url']),
                        disable_web_page_preview=False
                    )
                    sent_count += 1
                    
                    # Задержка между отправками, чтобы не превысить лимиты Telegram
                    await asyncio.sleep(0.05)
                    
                except Exception as e:
                    print(f"❌ Ошибка отправки пользователю {user_id}: {e}")
            
            # Сохраняем прогноз как отправленный
            self.db.add_sent_prediction(
                prediction['url'],
                prediction['title'],
                prediction['sport'],
                prediction['tournament']
            )
            
            print(f"📤 Прогноз отправлен {sent_count} пользователям: {prediction['title'][:50]}...")
            
        except Exception as e:
            print(f"❌ Ошибка при отправке прогноза: {e}")
    
    def _format_prediction_message(self, prediction: dict) -> str:
        """Форматировать сообщение с прогнозом"""
        sport_emoji = {
            'football': '⚽️',
            'hockey': '🏒',
            'basketball': '🏀',
            'tennis': '🎾',
        }
        
        emoji = sport_emoji.get(prediction['sport'], '🎯')
        
        message = (
            f"{emoji} <b>{prediction['title']}</b>\n\n"
            f"📅 Начало матча: {prediction['match_date']}\n\n"
            f"{prediction['description']}\n"
        )
        
        return message
    
    def stop(self):
        """Остановить планировщик"""
        self.scheduler.shutdown()
        print("🛑 Планировщик остановлен.")
