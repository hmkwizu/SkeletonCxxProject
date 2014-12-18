#!/usr/bin/env python
# encoding: utf-8

import errno
import functools
import os
import pipes
import subprocess
import sys

HERE = os.path.abspath(os.path.dirname(__file__))

sys.path.insert(1, os.path.join(HERE, 'third_party'))
import click

DirectoryPath = functools.partial(
    click.Path, file_okay=False, resolve_path=True)
FilePath = functools.partial(
    click.Path, dir_okay=False, resolve_path=True)

option = click.option
argument = click.argument


def shelljoin(args):
    return ' '.join(map(pipes.quote, args))


def which(command):
    if os.access(command, os.X_OK):
        return command

    for path in os.getenv('PATH', '').split(os.pathsep):
        abs_path = os.path.join(path, command)
        if os.access(abs_path, os.X_OK):
            return abs_path

    raise OSError(errno.ENOENT, 'Couldn\'t find {0}'.format(command))


def get_default_cmake_generator():
    try:
        which('ninja')
        return 'Ninja'
    except OSError:
        pass

    return 'Unix Makefiles'


@click.command()
@option('--prefix', type=DirectoryPath(), default='/usr/local',
        help='The installation prefix', show_default=True)
@option('--build-generator', default=get_default_cmake_generator,
        help='The build system generator used by CMake.', metavar='GENERATOR')
@option('--cc', 'c_compiler', default='cc', envvar='CC', show_default=True,
        help='The C compiler to use.', metavar='PROGRAM')
@option('--cxx', 'cxx_compiler', default='c++', envvar='CXX',
        metavar='PROGRAM', show_default=True, help='The C++ compiler to use.')
@option('--debug', 'build_type', flag_value='Debug', default=True)
@option('--release', 'build_type', flag_value='Release')
@option('--cmake', default='cmake', envvar='CMAKE', show_default=True,
        metavar='PROGRAM', help='The CMake program to use.')
@click.argument('extra_cmake_args', nargs=-1)
def cli(**kwargs):
    command = []
    command.extend([
        kwargs['cmake'],
        HERE,
        '--warn-uninitialized',
        '--no-warn-unused-cli',
        '-G{0}'.format(kwargs['build_generator']),
        '-DCMAKE_BUILD_TYPE={0}'.format(kwargs['build_type']),
        '-DCMAKE_INSTALL_PREFIX={0}'.format(kwargs['prefix']),
        '-DCMAKE_C_COMPILER={0}'.format(kwargs['c_compiler']),
        '-DCMAKE_CXX_COMPILER={0}'.format(kwargs['cxx_compiler']),
        '-DCMAKE_EXPORT_COMPILE_COMMANDS=1',
    ])
    command.extend(kwargs['extra_cmake_args'])

    echo_err = functools.partial(click.echo, err=True)
    echo_err('+ {0}'.format(shelljoin(command)))
    try:
        subprocess.check_call(command)
    except subprocess.CalledProcessError as e:
        sys.exit(e.returncode)

if __name__ == '__main__':
    cli()

