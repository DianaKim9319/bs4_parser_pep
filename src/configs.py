import logging
from logging.handlers import RotatingFileHandler
from argparse import ArgumentParser
from typing import KeysView as KeyV

from constants import BASE_DIR, LOG_FORMAT, DT_FORMAT, OutputType


def configure_argument_parser(available_modes: KeyV[str]) -> ArgumentParser:
    parser = ArgumentParser(description='Парсер документации Python')
    parser.add_argument(
        'mode',
        choices=available_modes,
        help='Режимы работы парсера'
    )
    parser.add_argument(
        '-c',
        '--clear-cache',
        action='store_true',
        help='Очистка кеша'
    )
    parser.add_argument(
        '-o',
        '--output',
        choices=tuple(enum.value for enum in OutputType),
        help='Дополнительные способы вывода данных'
    )
    return parser


def configure_logging() -> None:
    log_dir = BASE_DIR / 'logs'
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / 'parser.log'
    rotating_handler = RotatingFileHandler(
        log_file, maxBytes=10 ** 6, backupCount=5
    )
    logging.basicConfig(
        datefmt=DT_FORMAT,
        format=LOG_FORMAT,
        level=logging.INFO,
        handlers=(rotating_handler, logging.StreamHandler())
    )
