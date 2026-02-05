"""
Парсер прогнозов со Sports.ru
"""
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import re
from datetime import datetime
import config


class PredictionsParser:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def get_predictions_list(self) -> List[Dict]:
        """Получить список прогнозов с главной страницы"""
        try:
            response = self.session.get(config.PREDICTIONS_URL, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'lxml')
            predictions = []
            
            # Ищем блоки с прогнозами
            # На основе структуры страницы находим ссылки на прогнозы
            prediction_links = soup.select('a[href*="/predictions/"]')
            
            for link in prediction_links:
                href = link.get('href', '')
                
                # Проверяем, что это ссылка на конкретный прогноз
                if href and '/predictions/' in href and href.count('/') >= 3:
                    full_url = href if href.startswith('http') else f"{config.SPORTS_RU_URL}{href}"
                    
                    # Извлекаем вид спорта и ID из URL
                    sport_match = re.search(r'/predictions/([^/]+)/(\d+)', href)
                    if sport_match:
                        sport = sport_match.group(1)
                        prediction_id = sport_match.group(2)
                        
                        predictions.append({
                            'url': full_url,
                            'sport': sport,
                            'id': prediction_id
                        })
            
            # Убираем дубликаты
            seen = set()
            unique_predictions = []
            for pred in predictions:
                if pred['url'] not in seen:
                    seen.add(pred['url'])
                    unique_predictions.append(pred)
            
            return unique_predictions[:20]  # Берем последние 20
            
        except Exception as e:
            print(f"Ошибка при получении списка прогнозов: {e}")
            return []
    
    def parse_prediction(self, url: str) -> Optional[Dict]:
        """Парсить конкретный прогноз"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'lxml')
            
            # Извлекаем заголовок
            title_elem = soup.select_one('h1')
            title = title_elem.text.strip() if title_elem else ''
            
            # Извлекаем вид спорта из URL
            sport_match = re.search(r'/predictions/([^/]+)/', url)
            sport = sport_match.group(1) if sport_match else 'unknown'
            
            # Маппинг видов спорта на русском
            sport_mapping = {
                'football': 'football',
                'hockey': 'hockey',
                'basketball': 'basketball',
                'tennis': 'tennis',
            }
            sport_key = sport_mapping.get(sport, sport)
            
            # Извлекаем турнир из тегов или ссылок
            tournament = self._extract_tournament(soup, title)
            
            # Извлекаем дату начала матча
            match_date = self._extract_match_date(soup)
            
            # Извлекаем краткое описание (первые 2 абзаца)
            description = self._extract_description(soup)
            
            # Извлекаем партнерскую ссылку
            partner_url = self._extract_partner_url(soup)
            
            return {
                'url': url,
                'title': title,
                'sport': sport_key,
                'tournament': tournament,
                'match_date': match_date,
                'description': description,
                'partner_url': partner_url or config.DEFAULT_PARTNER_URL,
            }
            
        except Exception as e:
            print(f"Ошибка при парсинге прогноза {url}: {e}")
            return None
    
    def _extract_tournament(self, soup: BeautifulSoup, title: str) -> str:
        """Извлечь название турнира"""
        # Сначала пробуем найти в тегах
        tags = soup.select('a[href*="/predictions/"]')
        for tag in tags:
            tag_text = tag.text.strip()
            # Проверяем, что это не вид спорта
            if tag_text and tag_text not in ['Футбол', 'Хоккей', 'Баскетбол', 'Теннис', 'Прогнозы']:
                return tag_text
        
        # Пробуем извлечь из заголовка (обычно турнир идет в начале)
        # Например: "Кубок Италии: шансы..."
        tournament_match = re.match(r'^([^:]+):', title)
        if tournament_match:
            return tournament_match.group(1).strip()
        
        return 'Неизвестный турнир'
    
    def _extract_match_date(self, soup: BeautifulSoup) -> str:
        """Извлечь дату начала матча"""
        # Ищем в тексте паттерны даты
        text = soup.get_text()
        
        # Паттерны: "5 февраля 2026", "Начало: 23:00"
        date_patterns = [
            r'(\d{1,2}\s+(?:января|февраля|марта|апреля|мая|июня|июля|августа|сентября|октября|ноября|декабря)\s+\d{4})',
            r'Начало[:\s]+(\d{1,2}:\d{2})',
        ]
        
        date_parts = []
        for pattern in date_patterns:
            match = re.search(pattern, text)
            if match:
                date_parts.append(match.group(1))
        
        if date_parts:
            return ', '.join(date_parts)
        
        return 'Дата не указана'
    
    def _extract_description(self, soup: BeautifulSoup) -> str:
        """Извлечь краткое описание (первые 2 абзаца)"""
        # Ищем основной контент статьи
        content_div = soup.select_one('article, .article-content, .post-content')
        
        if not content_div:
            # Если не нашли, берем все параграфы
            paragraphs = soup.find_all('p')
        else:
            paragraphs = content_div.find_all('p')
        
        # Собираем первые 2 значимых абзаца (длиннее 100 символов)
        description_parts = []
        for p in paragraphs:
            text = p.get_text().strip()
            # Пропускаем короткие абзацы и рекламу
            if len(text) > 100 and 'Реклама' not in text and 'букмекер' not in text.lower()[:50]:
                description_parts.append(text)
                if len(description_parts) >= 2:
                    break
        
        description = '\n\n'.join(description_parts)
        
        # Ограничиваем длину
        if len(description) > config.MAX_DESCRIPTION_LENGTH:
            description = description[:config.MAX_DESCRIPTION_LENGTH] + '...'
        
        return description if description else 'Описание недоступно'
    
    def _extract_partner_url(self, soup: BeautifulSoup) -> Optional[str]:
        """Извлечь партнерскую ссылку из виджета прогноза"""
        # Ищем ссылки на spnsrd.ru
        partner_links = soup.select('a[href*="spnsrd.ru"]')
        
        for link in partner_links:
            href = link.get('href', '')
            # Берем первую подходящую ссылку
            if 'spnsrd.ru' in href:
                return href
        
        return None
    
    def get_new_predictions(self, already_sent_urls: set) -> List[Dict]:
        """Получить новые прогнозы, которые еще не были отправлены"""
        predictions_list = self.get_predictions_list()
        new_predictions = []
        
        for pred_info in predictions_list:
            if pred_info['url'] not in already_sent_urls:
                # Парсим полную информацию о прогнозе
                full_prediction = self.parse_prediction(pred_info['url'])
                if full_prediction:
                    new_predictions.append(full_prediction)
        
        return new_predictions
