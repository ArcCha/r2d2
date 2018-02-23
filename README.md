# r2d2

Simple utility program to help with managing central, git based configuration of your machine.

# How it works

In you home directory r2d2 creates its own folder together with git repository in it - `.r2d2`. It then uses it to store all you config files that you decide to manage with r2d2. When file is added to r2d2 it moves its content to `.r2d2` and creates symlink in place of the original file. Thanks to that, you can keep all your configuration files in one place and keep them safe easily with git.

# Examples

## Initialize empty instance of r2d2

```
./main.py init
```

This command will create `~/.r2d2` directory and initialize empty git repository in it.

## Add config file to r2d2

```
./main.py add file
```

This command will move the contents of `file` into `~/.r2d2` directory preserving the full path of `file` (`~/.r2d2` will be treated as a prefix) and stage it in the repository.
