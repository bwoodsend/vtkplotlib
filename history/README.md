# History

The changelog is updated on release.
Please do not add news entries for pull requests.

## Generation instructions:

Run in fish:

```fish
git log (git log --grep "Release v" -n1 --pretty="%H").. --pretty="* %B" > history/(python setup.py --version).rst
```

Prune out anything not relevant to end users, fixup reST syntax then check it
in.
Rebuild the docs to verify.
