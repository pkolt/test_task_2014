#!/usr/bin/env python
import re
import os
import sys
import textwrap
import lxml.html
import lxml.html.clean
import lxml.etree

from html.parser import HTMLParser
from urllib.parse import urlsplit
from urllib.request import urlopen, URLError, Request


__version__ = '0.0.1'
__author__ = 'Pavel Koltyshev <pkoltyshev@gmail.com>'

__all__ = ('WebPageError', 'WebPage', 'HTMLCleaner', 'Application', 'url_to_filepath')


HTTP_USER_AGENT = 'Mozilla/5.0 (Windows; I; Windows NT 5.1; ru; rv:1.9.2.13) Gecko/20100101 Firefox/4.0'
PATT_HTTP_CONTENT_TYPE = re.compile(r'([a-z0-9-/]+)\s?;\s?charset=([a-z0-9-]+)', re.I)


def url_to_filepath(url, ext='.txt'):
    """
    Преобразуют URL адрес в относительный путь к файлу.
    """
    urlobj = urlsplit(url)
    hostname = urlobj.hostname
    path = urlobj.path
    parts = list(filter(lambda v: v, path.strip('/').split('/')))
    if parts:
        part = parts.pop()
        if '.' in part:
            name = part.rsplit('.', 1)[0]
            parts.append(name + ext)
        else:
            parts.extend([part, 'index' + ext])
    else:
        parts = ['index' + ext]
    parts.insert(0, hostname)
    return '/'.join(parts)


class WebPageError(Exception):
    pass


class WebPage(object):
    user_agent = HTTP_USER_AGENT
    allow_mime_types = ('text/html', 'text/xhtml')

    @property
    def encoding(self):
        return self._encoding

    @property
    def content(self):
        return self._content

    @property
    def url(self):
        return self._real_url

    def __init__(self, url):
        self._open_url = url if url.startswith('http') else 'http://%s' % url

        req = Request(self._open_url, headers={'User-Agent': self.user_agent})
        try:
            resp = urlopen(req)
        except URLError:
            raise WebPageError('Невозможно открыть веб-страницу. Проверьте URL: %s' % self._open_url)

        stat_code = resp.getcode()
        if stat_code != 200:
            raise WebPageError('Невозможно открыть веб-страницу. Код ответа сервера: %d' % stat_code)

        self._real_url = resp.geturl()

        content_type = resp.info().get('content-type')
        mobj = re.search(PATT_HTTP_CONTENT_TYPE, content_type)
        if not mobj:
            raise WebPageError('Невозможно определить кодировку для страницы. Content-Type: %s' % content_type)
        self._mime_type, self._encoding = mobj.groups()

        if not self._mime_type in self.allow_mime_types:
            raise WebPageError('Загруженное содержимое не является веб-страницей. MIME тип: %s' % self._mime_type)

        try:
            self._content = resp.read().decode(self._encoding)
        except UnicodeDecodeError:
            raise WebPageError('Невозможно прочитать содержимое страницы в кодировке: %s' % self._encoding)


class HTMLCleaner(lxml.html.clean.Cleaner):
    scripts = True
    javascript = True
    comments = True
    style = True
    links = True
    meta = True
    page_structure = True
    processing_instructions = True
    embedded = True
    frames = True
    forms = True
    annoying_tags = True
    remove_tags = None
    kill_tags = ()
    allow_tags = ('a', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p')
    remove_unknown_tags = False
    safe_attrs_only = False
    safe_attrs = False
    add_nofollow = False
    host_whitelist = ()
    whitelist_tags = ()


class Application:
    """
    Программа для извлечения текста публикации из веб-страницы.

    Использование:
      python grabber.py url [параметры]

    Параметры:
      -p, --print   : Выводит результат в консоль.
      -h, --help    : Вызов справки.
      -v, --version : Отображает версию программы.
    """

    # Ограничивает длину текстовой строки при форматировании.
    # Длинные строки разбиваются по словам.
    text_format_width = 80

    def __init__(self, argv):
        self._webpage = None
        self._print = False
        self._argv = argv

    def main(self):
        argv = self._argv
        find_opts = lambda opts: any([name in argv[1:] for name in opts])

        if find_opts(['-p', '--print']):
            self._print = True

        if find_opts(['-h', '--h']):
            print(textwrap.dedent(self.__doc__))
        elif find_opts(['-v', '--version']):
            print('v%s' % __version__)
        else:
            try:
                url = argv[1]
            except IndexError:
                print('Не передан аргумент URL.')
            else:
                try:
                    self.process(url)
                except WebPageError as exc:
                    print(exc)

    def get_webpage_content(self, url):
        """
        Возвращает контент веб-страницы в виде HTML-разметки.
        """
        self._webpage = WebPage(url)
        return self._webpage.content

    def get_article_content(self, html):
        """
        Возвращает контент публикации в виде HTML-разметки.
        """
        is_header = lambda tag: re.match(r'h(1|2|3|4|5|6)', tag)

        tree = lxml.html.document_fromstring(html)
        body = tree.find('body')
        article = []
        for elem in body.iter('h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p'):
            if elem.text and elem.text.strip():
                if is_header(elem.tag):
                    if article:
                        prev_elem = article[-1]
                        if prev_elem.tag == 'p':
                            article.append(elem)
                    else:
                        article.append(elem)
                else:
                    article.append(elem)
            elif elem.tag == 'p':
                span = elem.find('span')
                if span is not None and span.text and span.text.strip() and len(span.text.strip().split()) > 1:
                    span.tag = 'p'
                    article.append(span)
        # Убираем заголовки в конце списка
        while True:
            try:
                last = article.pop()
                if not is_header(last.tag):
                    article.append(last)
                    break
            except IndexError:
                break

        cleaner = HTMLCleaner()
        clean = lambda v: cleaner.clean_html(v)
        tostr = lambda v: lxml.html.tostring(v, encoding='unicode')
        return ''.join([tostr(clean(elem)) for elem in article])

    def content_strip_tags(self, html):
        """
        Очищает контент публикации от HTML-разметки и возвращает простой текст.
        """
        # Заменяем удвоенные пробелы одинарным
        html = re.sub(r' {2,}', ' ', html)
        # Удаляем символы перевода строки и табуляцию
        html = re.sub(r'[\r\n\t]+', '', html)
        # Удаляем пробелы между тегами
        html = re.sub(r'(</\w+>)\s+(<\w+[^>]*>)', r'\1\2', html)
        # Производим замену ссылок на: текст [ссылка]
        html = re.sub(r'''<a[^>]*href=['"]([^'"]+)['"][^>]*>([^<]+)</a>''', r'\2 [\1]', html)
        html = re.sub(r'''<a[^>]*>([^<]*)</a>''', r'\1', html)
        # К заголовкам и параграфам добавляем перевод строки
        html = re.sub(r'''<(h1|h2|h3|h4|h5|h6|p)[^>]*>([^<]*)</\1>''', r'\2' + os.linesep * 2, html)
        html = HTMLParser().unescape(html)
        return html.strip()

    def text_format(self, text):
        """
        Форматирует текст.
        """
        parts = re.split(r'[\r\n]+', text)
        parts = map(lambda v: textwrap.wrap(v, width=self.text_format_width), parts)
        return (os.linesep * 2).join(map(lambda v: os.linesep.join(v), parts))

    def text_save(self, fp, text):
        """
        Сохраняет текст в файл.
        """
        dirname = os.path.dirname(fp)
        if not os.path.isdir(dirname):
            os.makedirs(dirname)
        with open(fp, 'w') as f:
            f.write(text)

    def get_filepath(self):
        """
        Возвращает абсолютный путь для сохранения файла.
        """
        dirname = os.path.dirname(os.path.realpath(__file__))
        filepath = url_to_filepath(self._webpage.url)
        return os.path.join(dirname, filepath)

    def process(self, url):
        """
        Шаблонный метод описывающий алгоритм работы программы.
        """
        html = self.get_webpage_content(url)
        html = self.get_article_content(html)
        text = self.content_strip_tags(html)
        text = self.text_format(text)
        if self._print:
            # Необходимо приобразовывать кодировку строки в кодировку для потока вывода.
            # Иначе в Windows возникает исключение т.к. поток вывода имеет кодировку cp866,
            # встречая символы utf-8 отсутствующие в его таблице бросает исключение UnicodeEncodeError.
            print(text.encode(sys.stdout.encoding, errors='ignore').decode(sys.stdout.encoding))
        else:
            fp = self.get_filepath()
            self.text_save(fp, text)


if __name__ == '__main__':
    app = Application(sys.argv)
    app.main()
