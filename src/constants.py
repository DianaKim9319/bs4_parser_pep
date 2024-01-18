from pathlib import Path
from enum import Enum


MAIN_DOC_URL = 'https://docs.python.org/3/'
MAIN_PEP_URL = 'https://peps.python.org/'
BASE_DIR = Path(__file__).parent

EXPECTED_STATUS = {
    'A': ['Active', 'Accepted'],
    'D': ['Deferred'],
    'F': ['Final'],
    'P': ['Provisional'],
    'R': ['Rejected'],
    'S': ['Superseded'],
    'W': ['Withdrawn'],
    '': ['Draft', 'Active'],
}

LOG_FORMAT = '"%(asctime)s - [%(levelname)s] - %(message)s"'
DT_FORMAT = '%d.%m.%Y %H:%M:%S'
DATETIME_FORMAT = '%Y-%m-%d_%H-%M-%S'
ENCODING = 'utf-8'

# Шаблон для поиска версии и статуса:
VERSION_PATTERN = r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)'
# Шаблон для поиска нужного формата в тэгах:
PDF_A4_PATTERN = r'.+pdf-a4\.zip$'


class OutputType(Enum):
    PRETTY = 'pretty'
    FILE = 'file'


class HTMLTag:
    A = 'a'
    DIV = 'div'
    DL = 'dl'
    DT = 'dt'
    H1 = 'h1'
    SECTION = 'section'
    TABLE = 'table'
    TBODY = 'tbody'
    TD = 'td'
    UL = 'ul'
    LI = 'li'
    TR = 'tr'


class HTMLAttr:
    CLASS = 'class'
    UL = 'ul'
    ID = 'id'
    HREF = 'href'
