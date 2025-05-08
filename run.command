#!/bin/bash

# Переходим в директорию проекта
cd "$(dirname "$0")"

echo "🔍 Проверяю запущенные инстансы бота..."

# Ищем процессы Python которые запускают бота и убиваем их
BOT_PROCESSES=$(ps aux | grep -i "python.*tg_bot_pet911" | grep -v grep | awk '{print $2}')

if [ -n "$BOT_PROCESSES" ]; then
    echo "🔥 Найдены запущенные инстансы бота, убиваю их:"
    for pid in $BOT_PROCESSES; do
        echo "   Убиваю процесс $pid"
        kill -9 $pid
    done
    echo "✅ Старые процессы убиты"
else
    echo "✅ Запущенных инстансов бота не найдено"
fi

# Даем немного времени на завершение процессов
sleep 1

# Активируем виртуальное окружение
echo "🔧 Активирую виртуальное окружение..."
if [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d ".venv" ]; then
    source .venv/bin/activate
else
    echo "❌ Виртуальное окружение не найдено (ни venv, ни .venv)"
    echo "⚠️ Установите зависимости: pip install -r requirements.txt"
fi

# Запускаем нового бота
echo "🚀 Запускаю новый инстанс бота..."
python -m tg_bot_pet911.main

# Держим терминал открытым если произошла ошибка
echo "❌ Бот остановлен"
read -p "Нажмите Enter для закрытия окна..." 