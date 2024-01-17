import logging
import re
from urllib.parse import urljoin
from collections import defaultdict

import requests_cache
from tqdm import tqdm

from configs import configure_argument_parser, configure_logging
from constants import BASE_DIR, MAIN_DOC_URL, MAIN_PEP_URL, EXPECTED_STATUS
from outputs import control_output
from utils import find_tag, get_soup


def whats_new(session):
    """
    Собирает ссылки на статьи о нововведениях в Python.

    """
    whats_new_url = urljoin(MAIN_DOC_URL, 'whatsnew/')
    soup = get_soup(session, whats_new_url)

    main_div = find_tag(soup, 'section',
                        attrs={'id': 'what-s-new-in-python'})
    div_with_ul = find_tag(main_div, 'div',
                           attrs={'class': 'toctree-wrapper'})
    sections_by_python = div_with_ul.find_all('li',
                                              attrs={'class': 'toctree-l1'})

    results = [('Ссылка на статью', 'Заголовок', 'Редактор, Автор')]

    for section in tqdm(sections_by_python):
        version_a_tag = find_tag(section, 'a')
        href = version_a_tag['href']
        version_link = urljoin(whats_new_url, href)
        soup = get_soup(session, version_link)

        h1 = find_tag(soup, 'h1')
        dl = find_tag(soup, 'dl')
        dl_text = dl.text.replace('\n', ' ')

        results.append(
            (version_link, h1.text, dl_text)
        )

    return results


def latest_versions(session):
    """
    Собирает информацию о версиях и статусах Python.

    """
    soup = get_soup(session, MAIN_DOC_URL)

    sidebar = find_tag(soup, 'div',
                       attrs={'class': 'sphinxsidebarwrapper'})
    ul_tags = sidebar.find_all('ul')

    for ul in ul_tags:
        if 'All versions' in ul.text:
            a_tags = ul.find_all('a')
            break
    else:
        raise Exception('Ничего не нашлось')

    results = [('Ссылка на документацию', 'Версия', 'Статус')]
    pattern = r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)'

    for a_tag in tqdm(a_tags):
        link = a_tag['href']
        text_match = re.search(pattern, a_tag.text)
        if text_match is not None:
            version, status = text_match.groups()
        else:
            version, status = a_tag.text, ''
        results.append(
            (link, version, status)
        )

    return results


def download(session):
    """
    Скачивает архив с документацией Python на ваш локальный диск.

    """
    downloads_url = urljoin(MAIN_DOC_URL, 'download.html')
    soup = get_soup(session, downloads_url)

    table_tag = find_tag(soup, 'table',
                         attrs={'class': 'docutils'})
    pdf_a4_tag = find_tag(table_tag, 'a',
                          attrs={'href': re.compile(r'.+pdf-a4\.zip$')})

    pdf_a4_link = pdf_a4_tag['href']
    archive_url = urljoin(downloads_url, pdf_a4_link)

    filename = archive_url.split('/')[-1]
    downloads_dir = BASE_DIR / 'downloads'
    downloads_dir.mkdir(exist_ok=True)
    archive_path = downloads_dir / filename

    response = session.get(archive_url)
    with open(archive_path, 'wb') as file:
        file.write(response.content)

    logging.info(f'Архив был загружен и сохранён: {archive_path}')


def pep(session):
    """
    Парсит данные обо всех документах PEP,
    сравнивает статус на странице PEP со статусом в общем списке,
    считает количество PEP в каждом статусе и общее количество PEP.

    """
    soup = get_soup(session, MAIN_PEP_URL)

    main_section = find_tag(soup, 'section',
                            attrs={'id': 'numerical-index'})
    table = find_tag(main_section, 'table',
                     attrs={'class': 'pep-zero-table docutils align-default'})
    tbody_tag = find_tag(table, 'tbody')
    tr_tags = tbody_tag.find_all('tr')

    count_status = defaultdict(int)
    result = [('Статус', 'Количество')]

    for tr_tag in tqdm(tr_tags):
        first_td_tag = find_tag(tr_tag, 'td')
        link_td_tag = first_td_tag.find_next_sibling()
        link_td_a_tag = find_tag(link_td_tag, 'a')

        href = link_td_a_tag['href']
        pep_link = urljoin(MAIN_PEP_URL, href)
        soup = get_soup(session, pep_link)

        detail_tag = find_tag(soup, 'section', {'id': 'pep-content'})
        dl_tag = find_tag(detail_tag, 'dl',
                          {'class': 'rfc2822 field-list simple'})

        for tag in dl_tag:
            if tag.name == 'dt' and tag.text == 'Status:':
                detail_status = tag.next_sibling.next_sibling.string
                count_status[detail_status] += 1

                preview_status = tr_tag.find('td').get_text(strip=True)[1:]
                if detail_status not in EXPECTED_STATUS[preview_status]:
                    logging.info(
                        '\n'
                        'Несовпадающие статусы:\n'
                        f'{pep_link}\n'
                        f'Статус в карточке: {detail_status}\n'
                        f'Ожидаемые статусы: '
                        f'{EXPECTED_STATUS[preview_status]}\n'
                    )
    result.extend(list(count_status.items()))
    result.append(('Итого', sum(count_status.values())))

    return result


MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
    'pep': pep,
}


def main():
    configure_logging()
    logging.info('Парсер запущен!')

    arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())
    args = arg_parser.parse_args()
    logging.info(f'Аргументы командной строки: {args}')

    session = requests_cache.CachedSession()
    if args.clear_cache:
        session.cache.clear()
    parser_mode = args.mode
    results = MODE_TO_FUNCTION[parser_mode](session)
    if results is not None:
        control_output(results, args)
    logging.info('Парсер завершил работу.')


if __name__ == '__main__':
    main()
