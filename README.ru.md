# Визуализация Charybdis + Universal Ortho

Python 3.9+, без сторонних библиотек. Скрипт visualize_vial.py и шаблон keymap_template.html должны находиться рядом. HTML работает автономно, без сети и сервера.

Запуск из каталога проекта:

```sh
python3 scripts/visualize_vial.py output/current-brackets/c-brackets-Ortho.vil -o output/current-brackets/keymap.html
```

Для нового экспорта:

```sh
python3 scripts/visualize_vial.py /Users/stasklem/Desktop/c.vil -o output/my-keymap.html
```

Откройте полученный HTML в браузере двойным щелчком. Кнопки переключают слой, язык внутри Ortho (Caps Lock), Shift и видимость верхнего ряда. Щелчок по клавише показывает исходное назначение Vial. «Печать / PDF» печатает текущий вид.

По умолчанию читается установленная Universal Layout Ortho. Другой файл можно указать явно:

```sh
python3 scripts/visualize_vial.py output/current-brackets/c-brackets-Ortho.vil --keylayout "output/three-row-layout/Universal Layout Ortho Symbols.keylayout" -o output/ortho-symbols.html
```

Поддерживается матрица Charybdis 10×6, обычные коды клавиш, модификаторы (включая вложенные), LTn, переключение слоёв и комбо. Используются реальные XML-таблицы и правила модификаторов macOS; включая различие Shift+цифра в Ortho, русские буквы и скобки через Option. Подписи над клавишами — физические QWERTY-позиции.

Ограничения: условная плоская геометрия; один выбранный слой поверх BASE; комбо подписаны по физическим QWERTY-кодам; макросы, tap dance, пользовательские обработчики прошивки и XML actions/dead keys не исполняются. Неизвестные коды показаны явно янтарным цветом. Состояние реальной клавиатуры не отслеживается. Используется первый набор геометрии macOS из keylayout. Cmd/Ctrl отображаются как сочетания, а не текст.

Проверки:

```sh
python3 -m unittest discover -s scripts -p 'test_*.py'
```

Проверены скобки в RU/EN, символы и цифры Ortho, удержания, сочетания и прозрачные клавиши. Браузерный просмотр в среде агента недоступен: политика браузера блокирует локальные file:// страницы. Поэтому внешний вид и печать требуют проверки в обычном браузере пользователя.
