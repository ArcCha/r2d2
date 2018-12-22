#!/usr/bin/env python
import argparse
import os
import pathlib
import shutil
import sys

import git
from git.exc import GitCommandError


def init(args):
    """Initialize r2d2, git-based repository in user's home directory.

    Accepted arguments:

    force -- removes `.r2d2` folder if it already exists.
    """
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
    """Add file to r2d2 repository and create symlink in it's place.

    Full file path is preserved under `.r2d2` folder so it can be
    easily identified and synced with live system.

    Accepted arguments:

    file - path to a file to be added.
    """
    r2d2_path = pathlib.Path.home().joinpath('.r2d2')
    file_path = pathlib.Path(args.file).resolve()
    target_path = r2d2_path.joinpath(file_path.relative_to('/'))
    if target_path.exists():
        print('File with same name is already managed by r2d2.')
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


def sync(args):
    """Syncs local repository with remotes.

    Accepted arguments:

    message - git commit message to be used if there is a need for a commit.
    """
    r2d2_path = pathlib.Path.home().joinpath('.r2d2')
    repo = git.Repo(path=str(r2d2_path))
    for remote in repo.remotes:
        remote.fetch()
        changes = repo.index.diff(None, staged=True)
        if changes:
            repo.index.commit(args.message)
        try:
            remote.pull(refspec='refs/heads/master:refs/heads/master')
        except GitCommandError:
            print('Pulling from remote ', str(remote), ' failed')
        remote.push(refspec='refs/heads/master:refs/heads/master')


def add_remote(args):
    """Add remote repository.

    Accepted arguments:

    name - remote name
    url - url pointing to remote repository
    """
    r2d2_path = pathlib.Path.home().joinpath('.r2d2')
    repo = git.Repo(path=str(r2d2_path))
    repo.create_remote(args.name, url=args.url)


def check_integrity(args):
    """Check if every file in r2d2 repository is correctly symlinked to live system.

    """
    r2d2_path = pathlib.Path.home().joinpath('.r2d2')
    for dirpath, dirnames, filenames in os.walk(r2d2_path):
        if dirpath.startswith(str(r2d2_path / '.git')):
            continue
        for filename in filenames:
            file_path = pathlib.Path(dirpath) / filename
            symlink_path = pathlib.Path('/') / file_path.relative_to(r2d2_path)
            if not symlink_path.is_symlink():
                print(str(symlink_path) + ' is not a symlink.')


def main():
    parser = argparse.ArgumentParser(prog='r2d2')
    subparsers = parser.add_subparsers()

    parser_init = subparsers.add_parser('init')
    parser_init.add_argument('-f', '--force', action='store_true')
    parser_init.set_defaults(func=init)

    parser_add = subparsers.add_parser('add')
    parser_add.add_argument('file')
    parser_add.set_defaults(func=add)

    parser_sync = subparsers.add_parser('sync')
    parser_sync.add_argument('-m', '--message')
    parser_sync.set_defaults(func=sync)

    parser_remote = subparsers.add_parser('remote')
    parser_remote.add_argument('-n', '--name')
    parser_remote.add_argument('-u', '--url')
    parser_remote.set_defaults(func=add_remote)

    parser_check = subparsers.add_parser('check')
    parser_check.set_defaults(func=check_integrity)

    args = parser.parse_args()
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
