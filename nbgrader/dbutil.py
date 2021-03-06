"""Database utilities for nbgrader"""
# Based on jupyterhub.dbutil

import os
import sys
import tempfile
import shutil

from contextlib import contextmanager
from subprocess import check_call
from typing import Iterator

_here = os.path.abspath(os.path.dirname(__file__))

ALEMBIC_INI_TEMPLATE_PATH = os.path.join(_here, 'alembic.ini')
ALEMBIC_DIR = os.path.join(_here, 'alembic')


def write_alembic_ini(alembic_ini: str = 'alembic.ini', db_url: str = 'sqlite:///gradebook.db') -> None:
    """Write a complete alembic.ini from our template.
    Parameters
    ----------
    alembic_ini: str
        path to the alembic.ini file that should be written.
    db_url: str
        The SQLAlchemy database url, e.g. `sqlite:///gradebook.db`.
    """
    with open(ALEMBIC_INI_TEMPLATE_PATH) as f:
        alembic_ini_tpl = f.read()

    with open(alembic_ini, 'w') as f:
        f.write(
            alembic_ini_tpl.format(
                alembic_dir=ALEMBIC_DIR,
                db_url=db_url,
            )
        )


@contextmanager
def _temp_alembic_ini(db_url: str) -> Iterator[str]:
    """Context manager for temporary JupyterHub alembic directory
    Temporarily write an alembic.ini file for use with alembic migration scripts.
    Context manager yields alembic.ini path.
    Parameters
    ----------
    db_url:
        The SQLAlchemy database url, e.g. `sqlite:///gradebook.db`.
    Returns
    -------
    alembic_ini:
        The path to the temporary alembic.ini that we have created.
        This file will be cleaned up on exit from the context manager.
    """
    td = tempfile.mkdtemp()
    try:
        alembic_ini = os.path.join(td, 'alembic.ini')
        write_alembic_ini(alembic_ini, db_url)
        yield alembic_ini
    finally:
        shutil.rmtree(td)


def upgrade(db_url, revision='head'):
    """Upgrade the given database to revision.
    db_url: str
        The SQLAlchemy database url, e.g. `sqlite:///gradebook.db`.
    revision: str [default: head]
        The alembic revision to upgrade to.
    """
    with _temp_alembic_ini(db_url) as alembic_ini:
        check_call(
            ['alembic', '-c', alembic_ini, 'upgrade', revision]
        )


def _alembic(*args):
    """Run an alembic command with a temporary alembic.ini"""
    with _temp_alembic_ini('sqlite:///gradebook.db') as alembic_ini:
        check_call(
            ['alembic', '-c', alembic_ini] + list(args)
        )


if __name__ == '__main__':
    _alembic(*sys.argv[1:])
