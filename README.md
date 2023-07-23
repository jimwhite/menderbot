# Menderbot
AI-powered command line tool for working with legacy code. Based on the principles of the [Mechanized Mending Manifesto](https://mender.ai/docs/intro).

## Commands implemented (-ish):

* `menderbot ask`: Ask a question about a specific piece of code or concept
* `menderbot chat`: Interactively chat in the context of the current directory
* `menderbot commit`: Generate an informative commit message based on a changeset
* `menderbot diff`: Summarize the differences between two versions of a codebase

## Commands (coming soon):

* `menderbot doc`: Generate documentation for the existing code
* `menderbot review`: Review a code block or changeset and provide feedback

## Developing

```
pipenv shell

python -m menderbot.build_treesitter
```
### Running
```
python -m menderbot
```
### Pre-commit

```
black menderbot
pylint --errors-only menderbot
pytest
```