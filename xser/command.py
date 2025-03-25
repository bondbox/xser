# coding:utf-8

from typing import Optional
from typing import Sequence

from xkits import add_command
from xkits import argp
from xkits import commands
from xkits import run_command

from xser.attribute import __description__
from xser.attribute import __project__
from xser.attribute import __urlhome__
from xser.attribute import __version__


@add_command(__project__, description=__description__)
def add_cmd(_arg: argp):
    pass


@run_command(add_cmd)
def run_cmd(cmds: commands) -> int:
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    cmds = commands()
    cmds.version = __version__
    return cmds.run(root=add_cmd, argv=argv, epilog=f"For more, please visit {__urlhome__}.")  # noqa:E501
