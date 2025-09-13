import logging
import sys
from pathlib import Path
from typing import Any

import click
import pydantic

from ..._compat import PYDANTIC_V2
from ...generator.models import InterfaceChoices
from .. import options, prisma
from ..utils import EnumChoice, PathlibPath, warning

ARG_TO_CONFIG_KEY = {
    'partials': 'partial_type_generator',
    'type_depth': 'recursive_type_depth',
}

log: logging.Logger = logging.getLogger(__name__)


# not sure why this type ignore is needed
@click.command('generate')  # type: ignore
@options.schema
@options.watch
@click.option(
    '--interface',
    type=EnumChoice(InterfaceChoices),
    help='Method that the client will use to interface with Prisma',
)
@click.option(
    '--partials',
    type=PathlibPath(exists=True, readable=True),
    help='Partial type generator location',
)
@click.option(
    '-t',
    '--type-depth',
    type=int,
    help='Depth to generate pseudo-recursive types to; -1 signifies fully recursive types',
)
@click.option(
    '--generator',
    multiple=True,
    help='Specifies which generator to use. Can be specified multiple times. By default, all generators will be ran',
)
def cli(
    schema: Path | None, watch: bool, generator: tuple[str], **kwargs: Any
) -> None:
    """Generate prisma artifacts with modified config options"""
    if pydantic.VERSION.split('.') < ['1', '8']:
        warning(
            'Unsupported version of pydantic installed, this command may not work as intended\n'
            'Please update pydantic to 1.8 or greater.\n'
        )

    args = ['generate']
    if schema is not None:
        args.append(f'--schema={schema}')

    if watch:
        args.append('--watch')

    if generator:
        for name in generator:
            args.append(f'--generator={name}')

    env: dict[str, str] = {}
    prefix = 'PRISMA_PY_CONFIG_'
    for key, value in kwargs.items():
        if value is None:
            continue

        env[prefix + ARG_TO_CONFIG_KEY.get(key, key).upper()] = serialize(
            key, value
        )

    log.debug('Running generate with env: %s', env)
    sys.exit(prisma.run(args, env=env))


def serialize(key: str, obj: Any) -> str:
    if not PYDANTIC_V2:
        if key == 'partials':
            # partials has to be JSON serializable
            return f'"{obj}"'
    return str(obj)
