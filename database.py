"""
Модуль для работы с базой данных
"""
import sqlite3
import json
from typing import List, Dict, Optional
from datetime import datetime


class Database:
    def __init__(self, db_path: str = 'predictions_bot.db'):
        self.db_path = db_path
        self.init_db()
    
    def get_connection(self):
        """Получить соединение с базой данных"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_db(self):
        """Инициализация базы данных"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Таблица пользователей
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Таблица подписок пользователей на виды спорта
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_sports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                sport TEXT,
                FOREIGN KEY (user_id) REFERENCES users (user_id),
                UNIQUE(user_id, sport)
            )
        ''')
        
        # Таблица подписок пользователей на турниры
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_tournaments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                sport TEXT,
                tournament TEXT,
                FOREIGN KEY (user_id) REFERENCES users (user_id),
                UNIQUE(user_id, sport, tournament)
            )
        ''')
        
        # Таблица отправленных прогнозов (чтобы не дублировать)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sent_predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prediction_url TEXT UNIQUE,
                title TEXT,
                sport TEXT,
                tournament TEXT,
                sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    # === Методы для работы с пользователями ===
    
    def add_user(self, user_id: int, username: str = None, 
                 first_name: str = None, last_name: str = None) -> bool:
        """Добавить нового пользователя"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR IGNORE INTO users (user_id, username, first_name, last_name)
                VALUES (?, ?, ?, ?)
            ''', (user_id, username, first_name, last_name))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Ошибка при добавлении пользователя: {e}")
            return False
    
    def get_user(self, user_id: int) -> Optional[Dict]:
        """Получить информацию о пользователе"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        user = cursor.fetchone()
        conn.close()
        return dict(user) if user else None
    
    def update_user_status(self, user_id: int, is_active: bool) -> bool:
        """Обновить статус активности пользователя"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE users 
                SET is_active = ?, updated_at = CURRENT_TIMESTAMP
                WHERE user_id = ?
            ''', (1 if is_active else 0, user_id))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Ошибка при обновлении статуса пользователя: {e}")
            return False
    
    def get_all_active_users(self) -> List[int]:
        """Получить всех активных пользователей"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT user_id FROM users WHERE is_active = 1')
        users = [row['user_id'] for row in cursor.fetchall()]
        conn.close()
        return users
    
    # === Методы для работы с подписками на виды спорта ===
    
    def add_user_sport(self, user_id: int, sport: str) -> bool:
        """Добавить подписку на вид спорта"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR IGNORE INTO user_sports (user_id, sport)
                VALUES (?, ?)
            ''', (user_id, sport))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Ошибка при добавлении подписки на спорт: {e}")
            return False
    
    def remove_user_sport(self, user_id: int, sport: str) -> bool:
        """Удалить подписку на вид спорта"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                DELETE FROM user_sports 
                WHERE user_id = ? AND sport = ?
            ''', (user_id, sport))
            # Также удаляем все подписки на турниры этого вида спорта
            cursor.execute('''
                DELETE FROM user_tournaments 
                WHERE user_id = ? AND sport = ?
            ''', (user_id, sport))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Ошибка при удалении подписки на спорт: {e}")
            return False
    
    def get_user_sports(self, user_id: int) -> List[str]:
        """Получить виды спорта пользователя"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT sport FROM user_sports WHERE user_id = ?', (user_id,))
        sports = [row['sport'] for row in cursor.fetchall()]
        conn.close()
        return sports
    
    def clear_user_sports(self, user_id: int) -> bool:
        """Очистить все подписки пользователя на виды спорта"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('DELETE FROM user_sports WHERE user_id = ?', (user_id,))
            cursor.execute('DELETE FROM user_tournaments WHERE user_id = ?', (user_id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Ошибка при очистке подписок: {e}")
            return False
    
    # === Методы для работы с подписками на турниры ===
    
    def add_user_tournament(self, user_id: int, sport: str, tournament: str) -> bool:
        """Добавить подписку на турнир"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR IGNORE INTO user_tournaments (user_id, sport, tournament)
                VALUES (?, ?, ?)
            ''', (user_id, sport, tournament))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Ошибка при добавлении подписки на турнир: {e}")
            return False
    
    def remove_user_tournament(self, user_id: int, sport: str, tournament: str) -> bool:
        """Удалить подписку на турнир"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                DELETE FROM user_tournaments 
                WHERE user_id = ? AND sport = ? AND tournament = ?
            ''', (user_id, sport, tournament))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Ошибка при удалении подписки на турнир: {e}")
            return False
    
    def get_user_tournaments(self, user_id: int, sport: str = None) -> List[str]:
        """Получить турниры пользователя (опционально по виду спорта)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        if sport:
            cursor.execute('''
                SELECT tournament FROM user_tournaments 
                WHERE user_id = ? AND sport = ?
            ''', (user_id, sport))
        else:
            cursor.execute('SELECT tournament FROM user_tournaments WHERE user_id = ?', (user_id,))
        tournaments = [row['tournament'] for row in cursor.fetchall()]
        conn.close()
        return tournaments
    
    # === Методы для работы с отправленными прогнозами ===
    
    def add_sent_prediction(self, prediction_url: str, title: str, 
                           sport: str, tournament: str) -> bool:
        """Добавить отправленный прогноз"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR IGNORE INTO sent_predictions (prediction_url, title, sport, tournament)
                VALUES (?, ?, ?, ?)
            ''', (prediction_url, title, sport, tournament))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Ошибка при добавлении отправленного прогноза: {e}")
            return False
    
    def is_prediction_sent(self, prediction_url: str) -> bool:
        """Проверить, был ли прогноз уже отправлен"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM sent_predictions WHERE prediction_url = ?', (prediction_url,))
        result = cursor.fetchone()
        conn.close()
        return result is not None
    
    def get_users_for_prediction(self, sport: str, tournament: str) -> List[int]:
        """Получить пользователей для отправки прогноза"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Пользователи, подписанные на этот вид спорта
        cursor.execute('''
            SELECT DISTINCT u.user_id 
            FROM users u
            JOIN user_sports us ON u.user_id = us.user_id
            WHERE u.is_active = 1 AND us.sport = ?
        ''', (sport,))
        
        sport_subscribers = [row['user_id'] for row in cursor.fetchall()]
        
        # Если у пользователя есть подписки на турниры, фильтруем
        filtered_users = []
        for user_id in sport_subscribers:
            cursor.execute('''
                SELECT COUNT(*) as count FROM user_tournaments 
                WHERE user_id = ? AND sport = ?
            ''', (user_id, sport))
            
            count = cursor.fetchone()['count']
            
            if count == 0:
                # Нет фильтра по турнирам - отправляем все
                filtered_users.append(user_id)
            else:
                # Проверяем, подписан ли на этот турнир
                cursor.execute('''
                    SELECT COUNT(*) as count FROM user_tournaments 
                    WHERE user_id = ? AND sport = ? AND tournament = ?
                ''', (user_id, sport, tournament))
                
                if cursor.fetchone()['count'] > 0:
                    filtered_users.append(user_id)
        
        conn.close()
        return filtered_users
