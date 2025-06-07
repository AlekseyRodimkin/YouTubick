#!/bin/bash

# docker run --rm   -v youtubick_shared_data:/app/uploads   alpine sh -c "\
#      mkdir -p /app/uploads && \
#      touch /app/uploads/test.txt && \
#      chown -R 1000:1000 /app/uploads && \
#      chmod -R u+rwX /app/uploads"

LOGS_VOLUME_NAME=youtubick_logs_data
UPLOADS_VOLUME_NAME=youtubick_shared_data
USER_ID=1000
GROUP_ID=1000

echo "----- Удаляем старый volume логов $LOGS_VOLUME_NAME (если есть)..."
docker volume rm "$LOGS_VOLUME_NAME" 2>/dev/null || echo "----- Volume $LOGS_VOLUME_NAME не существовал — пропускаем"

echo "----- Удаляем старый volume загрузок $UPLOADS_VOLUME_NAME (если есть)..."
docker volume rm "$UPLOADS_VOLUME_NAME" 2>/dev/null || echo "----- Volume $UPLOADS_VOLUME_NAME не существовал — пропускаем"

echo "----- Создаём volume $LOGS_VOLUME_NAME..."
docker volume create "$LOGS_VOLUME_NAME"

echo "----- Создаём volume $UPLOADS_VOLUME_NAME..."
docker volume create "$UPLOADS_VOLUME_NAME"

echo "----- Создаём директории и лог-файлы + выставляем владельца $USER_ID:$GROUP_ID..."
docker run --rm \
  -e UID="$USER_ID" \
  -e GID="$GROUP_ID" \
  -v "$LOGS_VOLUME_NAME":/app/logs \
  -v "$UPLOADS_VOLUME_NAME":/app/uploads \
  alpine sh -c "\
    mkdir -p /app/logs /app/uploads && \
    touch /app/logs/app_debug.log /app/logs/app_error.log && \
    chown -R \$UID:\$GID /app/logs /app/uploads && \
    chmod -R u+rwX /app/uploads /app/logs"

echo "----- Удаляем образ alpine (если он не используется)..."
docker rmi alpine 2>/dev/null || echo "----- Образ alpine используется и не может быть удалён сейчас"

echo "----- Готово -----"
