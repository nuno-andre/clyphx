# Contributing to ClyphX

## Vendorized packages

| package           | version | description |
| ----------------- | ------- | ----------- |
| [`python-future`] | 0.18.2  | Compability layer between Python 2.7 and Python 3
| [`typing`]        | 3.7.4.3 | Backport of the `typing` built-in module for Python 2.7
| [`retoken`]       | -       | Regex lexer

[`python-future`]: https://github.com/PythonCharmers/python-future
[`typing`]: https://github.com/python/typing
[`retoken`]: https://github.com/nuno-andre/python-regex-scanner

## VSCode

Rename `.vscode/.settings.json` to `.vscode/settings.json`.

### VSCode Tasks

<kbd>Shift</kbd>+<kbd>Ctrl</kbd>+<kbd>P</kbd> &rarr; _Tasks: Run tasks_

| task             | description |
| ---------------- | ----------- |
| `(re)start Live` | Restart Live, or start it if closed.
| `open Log.txt`   | Open Live's `Log.txt` with the system default application for txt files.

## Testing

```
pytest tests/<file>::test
```