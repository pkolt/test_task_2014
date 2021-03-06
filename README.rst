============
Site grabber
============

Программа для извлечения текста публикации из веб-страницы.

Системные требования
====================

* Python >= 3.3
* lxml >= 3.1

Описание программы
==================

Программа загружает веб-страницу по указанному URL.

Обрабатывает данные этой страницы, извлекая текст публикации.

Результат работы программы сохраняется в файл. Имя файла формируется по URL адресу.

Алготим работы программы
========================

+----+----------------------------------------------------------+----------------+-----------------+
| #  | Шаг алгоритма                                            | Входные данные | Выходные данные |
+====+==========================================================+================+=================+
| 1. | Загрузка веб-страницы по указанному URL.                 | URL страницы   | HTML-разметка   |
+----+----------------------------------------------------------+----------------+-----------------+
| 2. | Находит и распознает полезный контент на странице.       | HTML-разметка  | HTML-разметка   |
+----+----------------------------------------------------------+----------------+-----------------+
| 3. | Очистка контента от HTML-тегов.                          | HTML-разметка  | простой текст   |
+----+----------------------------------------------------------+----------------+-----------------+
| 4. | Форматирование текста.                                   | простой текст  | простой текст   |
+----+----------------------------------------------------------+----------------+-----------------+
| 5. | Сохранение текста в файл.                                | простой текст  | файл на диске   |
+----+----------------------------------------------------------+----------------+-----------------+

Программа тестировалась на сайтах
=================================

* Lenta.ru `http://lenta.ru/news/2014/02/21/dark/ <http://lenta.ru/news/2014/02/21/dark/>`_ -> `Результат работы <tests_result/lenta.txt>`_
* Uralweb.ru `http://www.uralweb.ru/news/business/421853.html <http://www.uralweb.ru/news/business/421853.html>`_ -> `Результат работы <tests_result/uralweb.txt>`_
* E1.ru `http://www.e1.ru/news/spool/news_id-401630-section_id-37.html <http://www.e1.ru/news/spool/news_id-401630-section_id-37.html>`_ -> `Результат работы <tests_result/e1.txt>`_


Использование и запуск
======================

``python grabber.py <url>``

Вывод результата работы программы на экран
------------------------------------------

``python grabber.py --print``

Вывод справки
-------------

``python grabber.py --help``

Вывод версии программы
----------------------

``python grabber.py --version``
