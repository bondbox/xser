# coding:utf-8

from typing import Optional
from typing import Sequence

from xkits_command import ArgParser
from xkits_command import Command
from xkits_command import CommandArgument
from xkits_command import CommandExecutor

from xser.attribute import __description__
from xser.attribute import __project__
from xser.attribute import __urlhome__
from xser.attribute import __version__


@CommandArgument(__project__, description=__description__)
def add_cmd(_arg: ArgParser):
    pass


@CommandExecutor(add_cmd)
def run_cmd(cmds: Command) -> int:
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    cmds = Command()
    cmds.version = __version__
    return cmds.run(root=add_cmd, argv=argv, epilog=f"For more, please visit {__urlhome__}.")  # noqa:E501
