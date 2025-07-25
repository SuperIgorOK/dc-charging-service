# ⚡ DC Charging Service

Микросервис управления быстрыми DC зарядными станциями (до 240 кВт, до 3 коннекторов, CCS/CHAdeMO/GB/T).  
Поддерживает протокол OCPP 2.0.1, взаимодействие через MQTT, REST API и WebSocket.  
Система построена по принципам чистой архитектуры и микросервисного подхода.

## 🛠️ Стек технологий

- FastAPI  
- PostgreSQL + TimescaleDB  
- Redis OM  
- RabbitMQ  
- Celery + Beat  
- MQTT (paho.mqtt)  
- Docker + docker-compose  
- Pytest + coverage  
- GitHub Actions CI

## 📁 Структура проекта

apps/  
├── api/ — FastAPI роуты  
├── celery/ — задачи Celery (проверка доступности станций и др.)  
├── repositories/ — работа с БД (SQLAlchemy)  
├── schemas/ — Pydantic-схемы, в т.ч. Redis-модели  
├── services/ — бизнес-логика (OCPP, MQTT, станции, сессии)  
├── settings/ — конфигурация проекта  

## 🚀 Запуск проекта


### ⚙️ Переменные окружения
- Создай файл `.env` в корне проекта и заполните его подобно .env.example
- Клонировать репозиторий и переходить в корень проекта:  
```git clone https://github.com/SuperIgorOK/dc-charging-service.git```

- Далее запустите:

```docker-compose up --build  ```

Ссылки:  
- Swagger-документация: http://localhost:8000/docs  
- Adminer: http://localhost:8080

## 🧪 Тестирование

# Установка зависимостей  
pip install -r requirements.txt  

# Запуск тестов с покрытием  
coverage run -m pytest  
coverage report  

## 🔁 Фоновые задачи (Celery + Beat)

Периодически (каждые 1 мин):  
- Получает все станции из БД  
- Проверяет Redis (коннекторы станции)  
- Если все коннекторы не обновлялись > 2 минут → переводит станцию в статус offline  

## 📡 MQTT-топики

- stations/<station_id>/telemetry – показания тока, напряжения, температуры 
- stations/<station_id>/events – session_started / session_finished.  

## 🧵 REST API

- GET /stations/{station_id} — Текущее состояние станции и коннекторов  
- GET /stations/{id}/sessions — История сессий (фильтр по диапазону времени)  
- GET /health — Сервисчек для оркестратора

## 🔧 GitHub Actions CI

- Прогон pytest при каждом push  
- Отчёт по покрытию (coverage)   
