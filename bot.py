#!/usr/bin/env python3
"""
Server Control Telegram Bot
Управление сервером через Telegram
"""

import subprocess
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, Defaults, MessageHandler, filters

# ========== НАСТРОЙКИ ==========
# Импорт из config.py
try:
    from config import BOT_TOKEN, OWNER_ID, ALLOWED_USERS
except ImportError:
    print("❌ Ошибка: Создайте config.py или установите BOT_TOKEN")
    BOT_TOKEN = None
    OWNER_ID = 0
    ALLOWED_USERS = []

# ========== ЛОГИРОВАНИЕ ==========
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ========== ПРОВЕРКА ДОСТУПА ==========
def is_authorized(user_id):
    """Проверка доступа пользователя"""
    return user_id in ALLOWED_USERS

# ========== КОМАНДЫ ==========
async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Приветствие"""
    if not is_authorized(update.effective_user.id):
        await update.message.reply_text("❌ Доступ запрещён")
        return
    
    await update.message.reply_text(
        f"👋 Привет, {update.effective_user.first_name}!\n\n"
        "🛠️ **Команды управления сервером:**\n\n"
        "📊 **Информация:**\n"
        "/status - Статус сервера\n"
        "/services - Список служб\n"
        "/disk - Место на диске\n"
        "/ram - Использование RAM\n"
        "/logs - Последние логи\n"
        "/backups - Последние бэкапы\n\n"
        "⚙️ **Управление службами:**\n"
        "/restart <service> - Перезапустить службу\n"
        "/start <service> - Запустить службу\n"
        "/stop <service> - Остановить службу\n\n"
        "🔒 **Безопасность:**\n"
        "/fail2ban - Статус Fail2ban\n"
        "/ssh - Статус SSH\n\n"
        "🔄 **Бэкапы:**\n"
        "/backup - Создать бэкап\n\n"
        "❓ **Помощь:**\n"
        "/help - Список команд"
    )

async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Помощь"""
    if not is_authorized(update.effective_user.id):
        await update.message.reply_text("❌ Доступ запрещён")
        return
    
    help_text = """
📋 **Список команд:**

**📊 Информация:**
/status - Статус сервера (CPU, RAM, диск, uptime)
/services - Активные службы
/disk - Место на диске
/ram - Использование оперативной памяти
/logs [lines] - Последние логи (по умолчанию 10)
/backups - Последние бэкапы

**📈 Мониторинг:**
/top - Топ процессов по CPU
/network - Статистика сети (порты, интерфейсы)
/domains - Список доменов (nginx)

**⚙️ Управление службами:**
/restart <service> - Перезапустить службу
/start <service> - Запустить службу
/stop <service> - Остановить службу
/enable <service> - Включить в автозапуск
/disable <service> - Отключить из автозапуска
/logs <service> [lines] - Логи службы
/journal <service> [lines] - Журнал systemd службы

*Примеры:*
/restart telegrab
/stop unisignal
/start postgresql
/logs telegrab 50
/journal ssh 30

**🔒 Безопасность:**
/fail2ban - Статус Fail2ban (заблокированные IP)
/ssh - Статус SSH (активные сессии)

**💾 Бэкапы:**
/backup - Создать полный бэкап

**🔧 Система:**
/ping - Проверка связи
/whoami - Информация о пользователе
/help - Эта справка
"""
    await update.message.reply_text(help_text)

async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Статус сервера"""
    if not is_authorized(update.effective_user.id):
        await update.message.reply_text("❌ Доступ запрещён")
        return

    try:
        # Uptime
        uptime = subprocess.check_output(
            "/usr/bin/uptime -p",
            shell=True, env={'PATH': '/usr/bin:/usr/sbin:/bin:/sbin'}
        ).decode().strip()

        # Load average
        uptime_full = subprocess.check_output(
            "/usr/bin/uptime",
            shell=True, env={'PATH': '/usr/bin:/usr/sbin:/bin:/sbin'}
        ).decode().strip()
        load = uptime_full.split("load average:")[1].strip()

        # CPU info
        cpu = subprocess.check_output(
            "/usr/bin/nproc",
            shell=True, env={'PATH': '/usr/bin:/usr/sbin:/bin:/sbin'}
        ).decode().strip()

        # RAM
        free = subprocess.check_output(
            "/usr/bin/free -h",
            shell=True, env={'PATH': '/usr/bin:/usr/sbin:/bin:/sbin'}
        ).decode().strip()
        ram_line = free.split("\n")[1]

        # Disk
        disk = subprocess.check_output(
            "/bin/df -h / | /usr/bin/tail -1",
            shell=True, env={'PATH': '/usr/bin:/usr/sbin:/bin:/sbin'}
        ).decode().strip()
        disk_parts = disk.split()
        disk_used = disk_parts[2]
        disk_avail = disk_parts[3]
        disk_percent = disk_parts[4]

        status = f"""
🖥️ **Статус сервера**

⏱️ **Uptime:** {uptime}
📊 **Load Average:** {load}
🔢 **CPU Cores:** {cpu}

💾 **RAM:**
{ram_line}

💿 **Диск:**
Использовано: {disk_used}
Свободно: {disk_avail} ({disk_percent})

✅ Все службы работают нормально
"""
        await update.message.reply_text(status)
    except Exception as e:
        logger.error(f"Error in cmd_status: {e}")
        await update.message.reply_text(f"❌ Ошибка: {e}")

async def cmd_services(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Список служб"""
    if not is_authorized(update.effective_user.id):
        await update.message.reply_text("❌ Доступ запрещён")
        return

    try:
        services = ["ssh", "postgresql", "telegrab", "unisignal", "fail2ban", "ufw"]
        result = ""

        for service in services:
            try:
                status = subprocess.check_output(
                    f"/usr/bin/systemctl is-active {service}",
                    shell=True, stderr=subprocess.DEVNULL, env={'PATH': '/usr/bin:/bin'}
                ).decode().strip()
                icon = "✅" if status == "active" else "❌"
                result += f"{icon} **{service}:** {status}\n"
            except Exception as e:
                result += f"❓ **{service}:** неизвестно (ошибка: {e})\n"

        await update.message.reply_text(f"📋 **Службы:**\n\n{result}")
    except Exception as e:
        logger.error(f"Error in cmd_services: {e}")
        await update.message.reply_text(f"❌ Ошибка: {e}")

async def cmd_disk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Место на диске"""
    if not is_authorized(update.effective_user.id):
        await update.message.reply_text("❌ Доступ запрещён")
        return
    
    try:
        disk = subprocess.check_output(
            "/bin/df -h",
            shell=True, env={'PATH': '/usr/bin:/usr/sbin:/bin:/sbin'}
        ).decode().strip()
        await update.message.reply_text(f"💿 **Диск:**\n```\n{disk}\n```")
    except Exception as e:
        logger.error(f"Error in cmd_disk: {e}")
        await update.message.reply_text(f"❌ Ошибка: {e}")

async def cmd_ram(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Использование RAM"""
    if not is_authorized(update.effective_user.id):
        await update.message.reply_text("❌ Доступ запрещён")
        return
    
    try:
        ram = subprocess.check_output(
            "/usr/bin/free -h",
            shell=True, env={'PATH': '/usr/bin:/usr/sbin:/bin:/sbin'}
        ).decode().strip()
        await update.message.reply_text(f"💾 **RAM:**\n```\n{ram}\n```")
    except Exception as e:
        logger.error(f"Error in cmd_ram: {e}")
        await update.message.reply_text(f"❌ Ошибка: {e}")

async def cmd_logs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Последние логи"""
    if not is_authorized(update.effective_user.id):
        await update.message.reply_text("❌ Доступ запрещён")
        return

    try:
        lines = context.args[0] if context.args else "10"
        # Используем stderr=subprocess.STDOUT чтобы игнорировать exit code
        logs = subprocess.run(
            f"/usr/bin/journalctl -p 3 -xb --no-pager --lines={lines}",
            shell=True,
            capture_output=True,
            text=True,
            env={'PATH': '/usr/bin:/usr/sbin:/bin:/sbin'}
        ).stdout.strip()

        if not logs:
            logs = "✅ Ошибок не найдено"

        await update.message.reply_text(f"📝 **Логи (последние {lines}):**\n```\n{logs}\n```")
    except Exception as e:
        logger.error(f"Error in cmd_logs: {e}")
        await update.message.reply_text(f"❌ Ошибка: {e}")

async def cmd_backups(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Последние бэкапы"""
    if not is_authorized(update.effective_user.id):
        await update.message.reply_text("❌ Доступ запрещён")
        return

    try:
        backups = subprocess.check_output(
            "/bin/ls -lht /root/backups/ | /usr/bin/head -10",
            shell=True, env={'PATH': '/usr/bin:/usr/sbin:/bin:/sbin'}
        ).decode().strip()
        await update.message.reply_text(f"📦 **Последние бэкапы:**\n```\n{backups}\n```")
    except Exception as e:
        logger.error(f"Error in cmd_backups: {e}")
        await update.message.reply_text(f"❌ Ошибка: {e}")

async def cmd_restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Перезапуск службы"""
    if not is_authorized(update.effective_user.id):
        await update.message.reply_text("❌ Доступ запрещён")
        return
    
    if not context.args:
        await update.message.reply_text("❌ Укажите имя службы: /restart <service>")
        return
    
    service = context.args[0]
    
    try:
        subprocess.check_output(
            f"/usr/bin/systemctl restart {service}",
            shell=True, stderr=subprocess.STDOUT, env={'PATH': '/usr/bin:/bin'}
        ).decode()
        await update.message.reply_text(f"✅ Служба **{service}** перезапущена")
    except Exception as e:
        logger.error(f"Error in cmd_restart: {e}")
        await update.message.reply_text(f"❌ Ошибка перезапуска {service}: {e}")

async def cmd_start_service(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Запуск службы"""
    if not is_authorized(update.effective_user.id):
        await update.message.reply_text("❌ Доступ запрещён")
        return
    
    if not context.args:
        await update.message.reply_text("❌ Укажите имя службы: /start <service>")
        return
    
    service = context.args[0]
    
    try:
        subprocess.check_output(
            f"/usr/bin/systemctl start {service}",
            shell=True, stderr=subprocess.STDOUT, env={'PATH': '/usr/bin:/bin'}
        ).decode()
        await update.message.reply_text(f"✅ Служба **{service}** запущена")
    except Exception as e:
        logger.error(f"Error in cmd_start: {e}")
        await update.message.reply_text(f"❌ Ошибка запуска {service}: {e}")

async def cmd_stop_service(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Остановка службы"""
    if not is_authorized(update.effective_user.id):
        await update.message.reply_text("❌ Доступ запрещён")
        return
    
    if not context.args:
        await update.message.reply_text("❌ Укажите имя службы: /stop <service>")
        return
    
    service = context.args[0]
    
    try:
        subprocess.check_output(
            f"/usr/bin/systemctl stop {service}",
            shell=True, stderr=subprocess.STDOUT, env={'PATH': '/usr/bin:/bin'}
        ).decode()
        await update.message.reply_text(f"✅ Служба **{service}** остановлена")
    except Exception as e:
        logger.error(f"Error in cmd_stop: {e}")
        await update.message.reply_text(f"❌ Ошибка остановки {service}: {e}")

async def cmd_fail2ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Статус Fail2ban"""
    if not is_authorized(update.effective_user.id):
        await update.message.reply_text("❌ Доступ запрещён")
        return

    try:
        status = subprocess.check_output(
            "/usr/bin/fail2ban-client status",
            shell=True, env={'PATH': '/usr/bin:/usr/sbin:/bin:/sbin'}
        ).decode().strip()
        sshd = subprocess.check_output(
            "/usr/bin/fail2ban-client status sshd",
            shell=True, env={'PATH': '/usr/bin:/usr/sbin:/bin:/sbin'}
        ).decode().strip()

        await update.message.reply_text(f"🛡️ **Fail2ban:**\n```\n{status}\n\n{sshd}\n```")
    except Exception as e:
        logger.error(f"Error in cmd_fail2ban: {e}")
        await update.message.reply_text(f"❌ Ошибка: {e}")

async def cmd_ssh(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Статус SSH"""
    if not is_authorized(update.effective_user.id):
        await update.message.reply_text("❌ Доступ запрещён")
        return

    try:
        who = subprocess.check_output(
            "/usr/bin/who",
            shell=True, env={'PATH': '/usr/bin:/usr/sbin:/bin:/sbin'}
        ).decode().strip()
        sessions = subprocess.check_output(
            "/usr/bin/ss | /usr/bin/grep ssh | /usr/bin/wc -l",
            shell=True, env={'PATH': '/usr/bin:/usr/sbin:/bin:/sbin'}
        ).decode().strip()

        await update.message.reply_text(f"🔐 **SSH:**\n\n👥 **Активные сессии:** {sessions}\n```\n{who if who else 'Нет активных сессий'}\n```")
    except Exception as e:
        logger.error(f"Error in cmd_ssh: {e}")
        await update.message.reply_text(f"❌ Ошибка: {e}")

async def cmd_backup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Создать бэкап"""
    if not is_authorized(update.effective_user.id):
        await update.message.reply_text("❌ Доступ запрещён")
        return
    
    msg = await update.message.reply_text("🔄 Начинаю бэкап...")
    
    try:
        output = subprocess.check_output(
            "/root/scripts/backup-all.sh",
            shell=True, stderr=subprocess.STDOUT, env={'PATH': '/usr/bin:/bin'}
        ).decode()
        
        await msg.edit_text(f"✅ **Бэкап завершён:**\n```\n{output}\n```")
    except Exception as e:
        logger.error(f"Error in cmd_backup: {e}")
        await msg.edit_text(f"❌ Ошибка бэкапа: {e}")

async def cmd_top(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Топ процессов по CPU/RAM"""
    if not is_authorized(update.effective_user.id):
        await update.message.reply_text("❌ Доступ запрещён")
        return

    try:
        top = subprocess.check_output(
            "/usr/bin/ps aux --sort=-%cpu | /usr/bin/head -11",
            shell=True, env={'PATH': '/usr/bin:/usr/sbin:/bin:/sbin'}
        ).decode().strip()
        
        await update.message.reply_text(f"🔝 **Топ процессов (CPU):**\n```\n{top}\n```")
    except Exception as e:
        logger.error(f"Error in cmd_top: {e}")
        await update.message.reply_text(f"❌ Ошибка: {e}")

async def cmd_network(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Статистика сети"""
    if not is_authorized(update.effective_user.id):
        await update.message.reply_text("❌ Доступ запрещён")
        return

    try:
        # Интерфейсы
        interfaces = subprocess.check_output(
            "/sbin/ip -o link show | /usr/bin/awk '{{print $2}}'",
            shell=True, env={'PATH': '/usr/bin:/usr/sbin:/bin:/sbin'}
        ).decode().strip()
        
        # Статистика
        netstat = subprocess.check_output(
            "/bin/netstat -tulpn 2>/dev/null || /bin/ss -tulpn",
            shell=True, env={'PATH': '/usr/bin:/usr/sbin:/bin:/sbin'}
        ).decode().strip()[:3000]
        
        await update.message.reply_text(f"🌐 **Сеть:**\n\n**Интерфейсы:**\n```\n{interfaces}\n```\n**Порты:**\n```\n{netstat}\n```")
    except Exception as e:
        logger.error(f"Error in cmd_network: {e}")
        await update.message.reply_text(f"❌ Ошибка: {e}")

async def cmd_domains(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Список доменов (nginx)"""
    if not is_authorized(update.effective_user.id):
        await update.message.reply_text("❌ Доступ запрещён")
        return

    try:
        # Проверка nginx
        nginx_conf = "/etc/nginx/nginx.conf"
        sites = subprocess.check_output(
            f"/bin/grep -r 'server_name' /etc/nginx/sites-enabled/ 2>/dev/null || echo 'Nginx не настроен или нет sites-enabled'",
            shell=True, env={'PATH': '/usr/bin:/usr/sbin:/bin:/sbin'}
        ).decode().strip()
        
        await update.message.reply_text(f"🌐 **Домены:**\n```\n{sites if sites else 'Nginx не настроен'}\n```")
    except Exception as e:
        logger.error(f"Error in cmd_domains: {e}")
        await update.message.reply_text(f"❌ Ошибка: {e}")

async def cmd_service_logs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Логи конкретной службы"""
    if not is_authorized(update.effective_user.id):
        await update.message.reply_text("❌ Доступ запрещён")
        return

    if not context.args:
        await update.message.reply_text("❌ Укажите имя службы: /logs <service>\nПример: /logs telegrab")
        return

    service = context.args[0]
    lines = context.args[1] if len(context.args) > 1 else "50"

    try:
        logs = subprocess.run(
            f"/usr/bin/journalctl -u {service} --no-pager --lines={lines}",
            shell=True,
            capture_output=True,
            text=True,
            env={'PATH': '/usr/bin:/usr/sbin:/bin:/sbin'}
        ).stdout.strip()

        if not logs:
            logs = "✅ Записей не найдено"

        await update.message.reply_text(f"📝 **Логи {service} (последние {lines}):**\n```\n{logs}\n```")
    except Exception as e:
        logger.error(f"Error in cmd_service_logs: {e}")
        await update.message.reply_text(f"❌ Ошибка: {e}")

async def cmd_enable_service(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Включить службу в автозапуск"""
    if not is_authorized(update.effective_user.id):
        await update.message.reply_text("❌ Доступ запрещён")
        return

    if not context.args:
        await update.message.reply_text("❌ Укажите имя службы: /enable <service>")
        return

    service = context.args[0]

    try:
        subprocess.check_output(
            f"/usr/bin/systemctl enable {service}",
            shell=True, env={'PATH': '/usr/bin:/usr/sbin:/bin:/sbin'}
        ).decode()
        await update.message.reply_text(f"✅ Служба **{service}** включена в автозапуск")
    except Exception as e:
        logger.error(f"Error in cmd_enable: {e}")
        await update.message.reply_text(f"❌ Ошибка: {e}")

async def cmd_disable_service(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отключить службу из автозапуска"""
    if not is_authorized(update.effective_user.id):
        await update.message.reply_text("❌ Доступ запрещён")
        return

    if not context.args:
        await update.message.reply_text("❌ Укажите имя службы: /disable <service>")
        return

    service = context.args[0]

    try:
        subprocess.check_output(
            f"/usr/bin/systemctl disable {service}",
            shell=True, env={'PATH': '/usr/bin:/usr/sbin:/bin:/sbin'}
        ).decode()
        await update.message.reply_text(f"✅ Служба **{service}** отключена из автозапуска")
    except Exception as e:
        logger.error(f"Error in cmd_disable: {e}")
        await update.message.reply_text(f"❌ Ошибка: {e}")

async def cmd_journal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Журнал systemd службы"""
    if not is_authorized(update.effective_user.id):
        await update.message.reply_text("❌ Доступ запрещён")
        return

    if not context.args:
        await update.message.reply_text("❌ Укажите имя службы: /journal <service>")
        return

    service = context.args[0]
    lines = context.args[1] if len(context.args) > 1 else "30"

    try:
        logs = subprocess.run(
            f"/usr/bin/journalctl -u {service} --no-pager --lines={lines} -o cat",
            shell=True,
            capture_output=True,
            text=True,
            env={'PATH': '/usr/bin:/usr/sbin:/bin:/sbin'}
        ).stdout.strip()

        if not logs:
            logs = "✅ Записей не найдено"

        await update.message.reply_text(f"📰 **Журнал {service}:**\n```\n{logs}\n```")
    except Exception as e:
        logger.error(f"Error in cmd_journal: {e}")
        await update.message.reply_text(f"❌ Ошибка: {e}")

async def cmd_ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Проверка связи"""
    if not is_authorized(update.effective_user.id):
        await update.message.reply_text("❌ Доступ запрещён")
        return
    
    await update.message.reply_text("🏓 Понг! Сервер на связи ✅")

async def cmd_whoami(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Информация о пользователе"""
    if not is_authorized(update.effective_user.id):
        await update.message.reply_text("❌ Доступ запрещён")
        return
    
    user_info = f"""
👤 **Информация:**

**ID:** `{update.effective_user.id}`
**Имя:** {update.effective_user.first_name}
**Username:** @{update.effective_user.username or 'не указан'}
**Доступ:** {'✅ Разрешён' if is_authorized(update.effective_user.id) else '❌ Запрещён'}
"""
    await update.message.reply_text(user_info)

async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Неизвестная команда или текст"""
    if not is_authorized(update.effective_user.id):
        await update.message.reply_text("❌ Доступ запрещён")
        return
    
    # Получаем текст сообщения
    text = update.message.text or ""
    
    # Если это команда
    if text.startswith('/'):
        await update.message.reply_text(
            "❓ Неизвестная команда\n\n"
            "Используйте /help для списка доступных команд."
        )
    # Если это обычный текст
    else:
        await update.message.reply_text(
            "🤖 Я понимаю только команды!\n\n"
            "Отправьте /help для списка доступных команд."
        )

# ========== MAIN ==========
def main():
    """Запуск бота"""
    
    # Проверка токена
    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("❌ Ошибка: Установите BOT_TOKEN в config.py")
        return
    
    # Создание приложения с поддержкой Markdown
    application = Application.builder().token(BOT_TOKEN).defaults(Defaults(parse_mode='Markdown')).build()
    
    # Добавление обработчиков
    application.add_handler(CommandHandler("start", cmd_start))
    application.add_handler(CommandHandler("help", cmd_help))
    
    # Информация
    application.add_handler(CommandHandler("status", cmd_status))
    application.add_handler(CommandHandler("services", cmd_services))
    application.add_handler(CommandHandler("disk", cmd_disk))
    application.add_handler(CommandHandler("ram", cmd_ram))
    application.add_handler(CommandHandler("logs", cmd_logs))
    application.add_handler(CommandHandler("backups", cmd_backups))
    
    # Мониторинг
    application.add_handler(CommandHandler("top", cmd_top))
    application.add_handler(CommandHandler("network", cmd_network))
    application.add_handler(CommandHandler("domains", cmd_domains))
    
    # Управление службами
    application.add_handler(CommandHandler("restart", cmd_restart))
    application.add_handler(CommandHandler("start", cmd_start_service))
    application.add_handler(CommandHandler("stop", cmd_stop_service))
    application.add_handler(CommandHandler("enable", cmd_enable_service))
    application.add_handler(CommandHandler("disable", cmd_disable_service))
    application.add_handler(CommandHandler("logs", cmd_service_logs))
    application.add_handler(CommandHandler("journal", cmd_journal))
    
    # Безопасность
    application.add_handler(CommandHandler("fail2ban", cmd_fail2ban))
    application.add_handler(CommandHandler("ssh", cmd_ssh))
    
    # Бэкапы
    application.add_handler(CommandHandler("backup", cmd_backup))
    
    # Система
    application.add_handler(CommandHandler("ping", cmd_ping))
    application.add_handler(CommandHandler("whoami", cmd_whoami))
    
    # Обработчик неизвестных команд и текстовых сообщений
    application.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, unknown_command))
    application.add_handler(MessageHandler(filters.COMMAND, unknown_command))
    
    # Запуск
    print("🤖 Бот запущен...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
