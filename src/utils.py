import logging

from requests import RequestException, Response
from requests_cache.session import CachedSession
from bs4 import BeautifulSoup, Tag
from typing import Optional

from exceptions import ParserFindTagException
from constants import ENCODING


def get_response(session: CachedSession, url: str) -> Optional[Response]:
    try:
        response = session.get(url)
        response.encoding = ENCODING
        return response
    except RequestException:
        logging.exception(
            f'Возникла ошибка при загрузке страницы {url}',
            stack_info=True
        )


def get_soup(session: CachedSession, url: str) -> Optional[BeautifulSoup]:
    response = get_response(session, url)
    if response is not None:
        return BeautifulSoup(response.text, 'lxml')
    return None


def find_tag(soup: BeautifulSoup, tag: str, attrs=None) -> Tag:
    searched_tag = soup.find(tag, attrs=(attrs or {}))
    if searched_tag is None:
        error_msg = f'Не найден тег {tag} {attrs}'
        logging.error(error_msg, stack_info=True)
        raise ParserFindTagException(error_msg)
    return searched_tag
