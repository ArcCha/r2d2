#!/usr/bin/env python
import argparse
import git
import pathlib
import shutil
import sys


def init(args):
    r2d2_path = pathlib.Path.home().joinpath('.r2d2')
    if args.force:
        shutil.rmtree(r2d2_path)
    try:
        r2d2_path.mkdir()
    except FileExistsError:
        print('It appears that r2d2 is already present. '
              'Run with `-f` to override.')
        sys.exit(1)
    repo = git.Repo.init(r2d2_path)


def add(args):
    r2d2_path = pathlib.Path.home().joinpath('.r2d2')
    file_path = pathlib.Path(args.file).resolve()
    target_path = r2d2_path.joinpath(file_path.relative_to('/'))
    if target_path.exists():
        print('Config file with same name is already managed by r2d2.')
        sys.exit(1)
    target_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.rename(target_path)
    try:
        file_path.symlink_to(target_path)
    except FileExistsError:
        print('It appears that this file is already managed by r2d2.')
        sys.exit(1)
    repo = git.Repo(path=str(r2d2_path))
    repo.index.add([str(target_path)])


def main():
    parser = argparse.ArgumentParser(prog='r2d2')
    subparsers = parser.add_subparsers()

    parser_init = subparsers.add_parser('init')
    parser_init.add_argument('-f', '--force', action='store_true')
    parser_init.set_defaults(func=init)

    parser_add = subparsers.add_parser('add')
    parser_add.add_argument('file')
    parser_add.set_defaults(func=add)

    args = parser.parse_args()
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
