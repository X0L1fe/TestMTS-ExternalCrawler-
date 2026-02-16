# Краткая методичка по парсеру Кинопоиска (spider "filmer")

## Описание
Паук собирает данные о фильмах из топа-1000 Кинопоиска (20 страниц). Для обхода защиты используется **Playwright** с реальными куками, полученными после ручного прохождения капчи.

## Основные компоненты
- **Scrapy** + **scrapy-playwright**
- **Куки** – заранее скопированы из браузера после успешного входа/прохождения капчи
- **Заголовки** – имитируют реальный браузер Chrome
- **Задержки** – `download_delay=2` и дополнительный `wait_for_timeout(2000)` после загрузки

## Проблемы с капчей и их решение
Кинопоиск (Яндекс) активно защищается от ботов. При автоматическом запуске происходит редирект на страницу с капчей (SmartCaptcha).  
**Решение:**  
1. Первый запуск выполняется **вручную** с открытым браузером (`headless=False`).  
2. В открывшемся окне нужно нажать кнопку «Я не робот» и, если потребуется, решить капчу.  
3. После успешного прохождения куки сохраняются в профиле Playwright (или экспортируются и вставляются в код).  
4. Последующие запуски используют эти куки, и капча больше не появляется (по крайней мере, на время жизни сессии).

## Ошибка 400 при первом запуске
При первом обращении к странице часто возникает ошибка `400` (Bad Request) на промежуточных запросах Яндекса. Это нормально – Playwright продолжает выполнение, и после ручного прохождения капчи страница загружается корректно. В логах могут появляться ошибки таймаута, если не дождаться появления нужного селектора.

## Настройка и запуск
### 1. Установка зависимостей
```bash
pip install scrapy scrapy-playwright playwright
playwright install chromium
```

### 2. Настройка профиля Playwright (для сохранения кук)
В `settings.py` пропишите:
```python
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
ROBOTSTXT_OBEY = False
DOWNLOAD_HANDLERS = {
    "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
}

TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"

PLAYWRIGHT_BROWSER_TYPE = "chromium"
PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT = 30000  # мс
PLAYWRIGHT_NAVIGATION_TIMEOUT = 30000
PLAYWRIGHT_LAUNCH_OPTIONS = {
    "headless": False,
}
PLAYWRIGHT_CONTEXTS = {
    "default": {
        "persistent": True,
        "user_data_dir": r"C:\Users\light\AppData\Local\Google\Chrome\User Data\Default", 
        "headless": False,
        "viewport": {"width": 1280, "height": 800},
        "user_agent": "Mozilla/5.0 ...",
        "locale": "ru-RU",
    }
}
PLAYWRIGHT_LAUNCH_OPTIONS = {
    "headless": False,
    "args": [
        "--disable-blink-features=AutomationControlled", # Параметры для маскировки от распознания бота
        "--disable-features=VizDisplayCompositor",
        "--disable-gpu",
        "--no-sandbox",
        "--disable-web-security",
        "--disable-features=IsolateOrigins,site-per-process",
        "--disable-features=BlockInsecurePrivateNetworkRequests",
        "--disable-features=OutOfBlinkCors",
        "--disable-setuid-sandbox",
        "--disable-dev-shm-usage",
        "--disable-accelerated-2d-canvas",
        "--disable-accelerated-jpeg-decoding",
        "--disable-accelerated-mjpeg-decode",
        "--disable-accelerated-video-decode",
        "--disable-background-timer-throttling",
        "--disable-backgrounding-occluded-windows",
        "--disable-breakpad",
        "--disable-component-extensions-with-background-pages",
        "--disable-extensions",
        "--disable-features=TranslateUI,BlinkGenPropertyTrees",
        "--disable-ipc-flooding-protection",
        "--disable-renderer-backgrounding",
        "--enable-features=NetworkService,NetworkServiceInProcess",
        "--force-color-profile=srgb",
        "--hide-scrollbars",
        "--metrics-recording-only",
        "--mute-audio",
        "--no-first-run",
        "--no-zygote",
        "--safebrowsing-disable-auto-update",
        "--use-gl=angle",
        "--use-angle=gl",
    ],
}
```

### 3. Первый запуск (с капчей)
Запустите паука:
```bash
scrapy crawl filmer -o test.csv
```
В открывшемся окне браузера:
- Дождитесь появления капчи (если она есть).
- Нажмите «Я не робот» и выполните задание.
- После успешного прощения страница загрузится, и паук начнёт сбор данных.

### 4. Последующие запуски
После того как куки сохранились в профиле, можно включить `headless: True` в настройках (или оставить `headless: False` для отладки). Паук будет работать автоматически.

## Примечания по коду
- **Куки** вставлены прямо в код (словарь `cookies`). Если сессия истечёт, их нужно обновить (повторить шаг 1).
- **Селекторы** могут устареть – если данные не собираются, проверьте актуальные классы элементов на сайте через DevTools.
- **Задержки** подобраны эмпирически: `download_delay=2` и `wait_for_timeout(2000)` снижают нагрузку и повышают стабильность.

## Возможные ошибки и их устранение
| Ошибка | Причина | Решение |
|--------|---------|---------|
| `TimeoutError` при ожидании селектора | Страница не загрузилась полностью из-за капчи или медленного соединения | Увеличьте таймаут в `PageMethod` или добавьте более надёжный селектор. |
| Пустой CSV | Неправильные куки или селекторы | Проверьте куки (вставьте актуальные из браузера) и обновите классы. |
| Ошибка 400 в логах | Промежуточный запрос Яндекса | Игнорируйте – после капчи страница загружается. |
| Капча появляется снова | Сессия истекла или куки не сохранились | Повторите ручной вход с сохранением профиля. |

## Заключение
Парсер работает стабильно при условии актуальных кук и правильных селекторов. Основная сложность – первоначальное прохождение капчи, которое делается вручную. После этого сбор данных можно автоматизировать полностью.