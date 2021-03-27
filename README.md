# FastAPI REST API для магазина сладостей

<!-- TABLE OF CONTENTS -->
<details open="open">
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">О проекте</a>
    </li>
    <li>
      <a href="#getting-started">Развертывание</a>
    </li>
    <li><a href="#usage">Возможности</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## О проекте

Данные проект выполнен в рамках тестового задания для Школы Бэкенда от yandex
в 2021.

<!-- GETTING STARTED -->
## Развертывание

Для старта необходимо установить все зависимости и запустить приложение либо как пакет
```bash
python -m app
```
Либо импортировать приложение и самостоятельно запустить сервер.

```python
from app import app
import uvicorn
uvicorn.run(app, host="127.0.0.1", port=8080)
```

## Возможности

Сервис предоставляет возможности нанимать курьеров на работу,
iпринимать заказы и оптимально распределять заказы между курьерами, попутно считая их рейтинг и заработок.

Сервис перезагружается при рестарте машины посредством crontab.
Сервис поддерживает асинхронные запросы.

