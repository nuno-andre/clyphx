# Contributing to ClyphX


## Installing development environment

### Windows

```powershell
PS> git clone https://github.com/nuno-andre/clyphx.git
PS> cd clyphx
PS> . .\tools\win.ps1; install-runtime
PS> python3 .\tools\vscode.py
PS> install-dev-script
```


## Vendorized libs

| package | version | description |
| ------- | ------- | ----------- |
| [`python-future`](https://github.com/PythonCharmers/python-future) | 0.18.2 | Compability layer between Python 2.7 and Python 3 |


## VSCode tasks

<kbd>Shift</kbd>+<kbd>Ctrl</kbd>+<kbd>P</kbd> &rarr; _Tasks: Run tasks_

| task | description |
| ---- | ----------- |
| `(re)start Live` | Restart Live, or start it if closed.
| `open Log.txt`   | Open `Log.txt` with the default application for txt files.
