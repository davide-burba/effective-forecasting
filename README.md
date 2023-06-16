# Effective Forecasting

This repository contains the code tutorials for the [Effective Forecasting](https://effectiveforecasting.com) blog.

I use [Poetry](https://python-poetry.org) to manage dependencies. To execute the tutorials in the same environment, you can simply run:
```bash
poetry install --no-root
```
To make the virtual environment available as a jupyter kernel, you can run:
```bash
poetry run python -m ipykernel install --user --name=effective-forecasting
```

Some tutorials need different environments to be run; for these there are specific instructions in the README inside the tutorial folder.
