# Server Control Telegram Bot v1.0

Telegram-бот для администрирования сервера.

**Версия:** 1.0  
**Язык:** Python 3.12  
**Фреймворк:** python-telegram-bot 20.7

---

## 🚀 Быстрый старт

### 1. Создать бота в @BotFather

1. Откройте @BotFather в Telegram
2. Отправьте `/newbot`
3. Введите имя: `My Server Bot`
4. Введите username: `xloyvpacdg_bot` (должен заканчиваться на `bot`)
5. Скопируйте **API токен**

### 2. Узнать свой Telegram ID

**Способ 1: Через @userinfobot**
1. Откройте @userinfobot в Telegram
2. Нажмите Start
3. Скопируйте ваш **Id** (число, например `5610580916`)

**Способ 2: Через @RawDataBot**
1. Откройте @RawDataBot в Telegram
2. Нажмите Start
3. Найдите поле `"id": 5610580916`

**Способ 3: Вручную через бота**
После запуска бота отправьте `/whoami` — он покажет ваш ID.

### 3. Настроить конфигурацию

```bash
cd /root/git/server-bot
nano config.py
```

**Пример config.py:**
```python
# Server Bot Configuration

# ========== BOT TOKEN ==========
# Получите токен в @BotFather
BOT_TOKEN = "123456789:ABCdefGHIjklMNOpqrsTUVwxyz"

# ========== OWNER ID ==========
# Ваш Telegram ID (узнайте через @userinfobot)
OWNER_ID = 5610580916

# ========== ALLOWED USERS ==========
# Список Telegram ID пользователей с доступом
ALLOWED_USERS = [OWNER_ID]
```

Замените:
- `BOT_TOKEN` на ваш токен из @BotFather
- `OWNER_ID` на ваш ID из @userinfobot

**⚠️ Важно:** `config.py` содержит секреты — НЕ коммитьте в Git!

---

#### Добавить других пользователей:

```python
ALLOWED_USERS = [5610580916, 123456789, 987654321]
```

Просто добавьте их Telegram ID в список.

### 4. Установить зависимости

```bash
cd /root/git/server-bot
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 5. Установить службу

```bash
sudo cp server-bot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable server-bot
```

### 6. Запустить

```bash
sudo systemctl start server-bot
sudo systemctl status server-bot
```

---

## 📋 Все команды (22)

### 📊 Мониторинг и статистика

| Команда | Описание |
|---------|----------|
| `/top` | Топ процессов по CPU |
| `/network` | Статистика сети (интерфейсы, порты) |
| `/domains` | Список доменов nginx |
| `/status` | Полная информация о сервере |
| `/services` | Статус всех служб |
| `/disk` | Использование диска |
| `/ram` | Использование RAM |

### ⚙️ Управление службами

| Команда | Описание |
|---------|----------|
| `/restart <service>` | Перезапустить службу |
| `/start <service>` | Запустить службу |
| `/stop <service>` | Остановить службу |
| `/enable <service>` | Включить в автозапуск |
| `/disable <service>` | Отключить из автозапуска |
| `/logs <service> [lines]` | Логи службы (journalctl) |
| `/journal <service> [lines]` | Журнал systemd |

**Примеры:**
```
/restart telegrab
/stop unisignal
/start postgresql
/logs telegrab 50
/journal ssh 30
/enable postgresql
```

### 🔒 Безопасность

| Команда | Описание |
|---------|----------|
| `/fail2ban` | Статус Fail2ban, забаненные IP |
| `/ssh` | Активные SSH сессии |

### 💾 Бэкапы

| Команда | Описание |
|---------|----------|
| `/backup` | Создать полный бэкап |
| `/backups` | Список последних бэкапов |

### 🔧 Системные

| Команда | Описание |
|---------|----------|
| `/ping` | Проверка связи |
| `/whoami` | Информация о пользователе |
| `/reboot` | Перезагрузка сервера |
| `/help` | Справка по командам |
| `/start` | Приветствие |

---

## 🔐 Безопасность

- ✅ **Только авторизованные пользователи** (ALLOWED_USERS) могут управлять сервером
- ✅ **Парольная аутентификация отключена** (только SSH ключи)
- ✅ **Бот использует локальные команды** от root
- ✅ **Токен хранится в config.py** (НЕ коммитьте в Git!)
- ✅ **Markdown разметка** сообщений
- ✅ **Безопасная обработка ввода** (не повторяет пользовательские данные)
- ✅ **Валидация всех входных данных**

---

## 🛠️ Управление ботом

```bash
# Статус
sudo systemctl status server-bot

# Логи в реальном времени
sudo journalctl -u server-bot -f

# Перезапуск
sudo systemctl restart server-bot

# Остановка
sudo systemctl stop server-bot

# Автозапуск
sudo systemctl enable server-bot
```

---

## 📁 Структура проекта

```
/root/git/server-bot/
├── bot.py              # Основной код (670+ строк)
├── config.py           # Конфигурация (токен, ID) ⚠️ не коммить!
├── requirements.txt    # Зависимости Python
├── server-bot.service  # Systemd служба
├── .gitignore          # Git исключения
├── venv/              # Виртуальное окружение
└── README.md          # Документация
```

---

## 📦 Зависимости

```
python-telegram-bot==20.7
requests==2.31.0
```

---

## ⚠️ Важно

1. **НЕ коммитьте `config.py`** в Git — содержит токен бота!
2. **Сохраните токен** в надёжном месте (менеджер паролей)
3. **Добавляйте только доверенных пользователей** в `ALLOWED_USERS`
4. **Регулярно обновляйте** зависимости: `pip install --upgrade -r requirements.txt`
5. **Не передавайте пользовательский ввод** в ответы бота (защита от XSS)

---

## 🐛 Решение проблем

### Бот не отвечает
```bash
sudo systemctl status server-bot
sudo journalctl -u server-bot -n 50
```

### Ошибка токена
Проверьте `config.py` — токен должен быть без лишних кавычек

### Доступ запрещён
Проверьте `OWNER_ID` в config.py (должен совпадать с вашим Telegram ID)

### Команда не работает
Проверьте имя службы: `/usr/bin/systemctl list-units --type=service`

### Бот отвечает "Неизвестная команда"
Убедитесь, что команда введена правильно. Используйте `/help` для списка команд.

---

## 📊 Статистика проекта

| Метрика | Значение |
|---------|----------|
| **Команд** | 23 |
| **Строк кода** | 700+ |
| **Зависимостей** | 12 пакетов |
| **Версия** | 1.0 |

---

## 📞 Контакты

**Владелец:** JeBance  
**Telegram:** @JeBance  
**GitHub:** https://github.com/JeBance

---

## 📝 Лицензия

MIT License — свободное использование с указанием автора.
