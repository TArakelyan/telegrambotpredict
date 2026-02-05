# Шпаргалка - Быстрый деплой за 5 минут

## 📋 Чек-лист перед деплоем

- [ ] Есть аккаунт на GitHub
- [ ] Есть аккаунт на Render.com
- [ ] Токен бота от @BotFather: `8399906862:AAGztEPgwD6QgI2AOnKo0yF8_I8jYiOfpyY`

---

## 🚀 Быстрый деплой (без git)

### 1. GitHub (2 минуты)
1. Откройте [github.com](https://github.com) → **New repository**
2. Название: `telegram-predictions-bot`
3. **НЕ** добавляйте README, .gitignore, license
4. **Create repository**
5. Нажмите **"uploading an existing file"**
6. Перетащите ВСЕ файлы из папки `telegram-predictions-bot` (кроме `.env`)
7. Commit message: `Initial commit`
8. **Commit changes**

### 2. Render.com (3 минуты)
1. Откройте [render.com](https://render.com) → **New +** → **Web Service**
2. Подключите GitHub → выберите репозиторий `telegram-predictions-bot`
3. Заполните:
   - Name: `telegram-predictions-bot`
   - Runtime: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python bot.py`
   - Plan: **Free**
4. **Create Web Service**
5. После создания → вкладка **Environment** → **Add Environment Variable**:
   ```
   BOT_TOKEN = 8399906862:AAGztEPgwD6QgI2AOnKo0yF8_I8jYiOfpyY
   WEBHOOK_URL = https://ваш-сервис.onrender.com
   CHECK_INTERVAL = 300
   ```
6. **Save Changes**

### 3. Проверка (30 секунд)
1. Откройте вкладку **Logs** → дождитесь:
   ```
   ✅ Планировщик запущен
   ✅ Бот запущен и готов к работе!
   ```
2. В Telegram → найдите бота → `/start`
3. Работает! 🎉

---

## 📝 Важные ссылки

- Ваш бот: https://t.me/ваш_бот
- GitHub: https://github.com/ваш_username/telegram-predictions-bot
- Render: https://dashboard.render.com

---

## 🛠 Частые команды

### Обновить код
```bash
# В GitHub через веб-интерфейс:
1. Откройте файл
2. Нажмите карандаш (Edit)
3. Внесите изменения
4. Commit changes

# Render автоматически задеплоит новую версию
```

### Посмотреть логи
Render → ваш сервис → вкладка **Logs**

### Перезапустить
Render → ваш сервис → **Manual Deploy** → **Deploy latest commit**

### Проверить БД
Render → ваш сервис → **Shell** → `sqlite3 predictions_bot.db`

---

## ⚙️ Переменные окружения

| Переменная | Значение | Описание |
|------------|----------|----------|
| `BOT_TOKEN` | `8399906862:AAGztEP...` | Токен от @BotFather |
| `WEBHOOK_URL` | `https://app.onrender.com` | URL вашего Render сервиса |
| `CHECK_INTERVAL` | `300` | Интервал проверки (сек) |

---

## 🐛 Быстрое решение проблем

### Бот не отвечает
✅ Проверьте статус сервиса (должен быть "Live")
✅ Проверьте логи на ошибки
✅ Убедитесь, что `BOT_TOKEN` правильный

### Не приходят прогнозы
✅ Отправьте `/start` и выберите виды спорта
✅ Подождите 5 минут (интервал проверки)
✅ Проверьте логи: должно быть "🔍 Проверяю новые прогнозы..."

### Сервис засыпает
✅ Используйте [UptimeRobot](https://uptimerobot.com) (бесплатно)
✅ Или upgrade на платный план ($7/мес)

---

## 📊 Команды бота

- `/start` - Начать работу
- `/settings` - Настроить подписки
- `/stop` - Отключить уведомления
- `/help` - Справка

---

## 🎯 Что дальше?

1. ✅ Бот работает на Render
2. 📱 Протестируйте все команды
3. 👥 Пригласите пользователей
4. 📈 Следите за метриками в Render
5. 🔧 Настройте UptimeRobot (чтобы не засыпал)

---

## 📚 Полная документация

- `README.md` - Обзор проекта
- `DEPLOY.md` - Подробная инструкция по деплою
- `QUICKSTART.md` - Локальное тестирование
- `FAQ.md` - Часто задаваемые вопросы

---

**Готово! Ваш бот работает 24/7! 🎉**

*Нужна помощь? Проверьте FAQ.md или логи на Render*
