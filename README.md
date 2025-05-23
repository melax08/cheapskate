# cheapskate - telegram bot and API for financial control

[![Actions status](https://github.com/melax08/cheapskate/actions/workflows/cheapskate-workflow.yml/badge.svg)](https://github.com/melax08/cheapskate/actions)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

## Information

### Description

Telegram bot and REST API for convenient control of your expenses and obtaining convenient statistics on spending.

### Features

- REST API with swagger documentation, allows to connect backend to your custom interface like mobile apps, sites, etc;
- Telegram bot that provides a convenient interface for managing expenses;
- Ability to add categories of expenses, which will be displayed as a keyboard in the bot when adding expenses;
- Ability to add and remove expenses by category from the list of previously added ones;
- Currencies system (add currency, show expenses by currencies and categories);
- Settings to set default currency and month budget;
- Various options to get statistics on spending (today's spending, remaining money for the month, statistics by month and years, etc.);
- Authentication system;
- Error handling and logging;
- Asynchronous interaction between telegram bot and API.

### Author

Ilya Malashenko (github: melax08, telegram: @ScreamOFF)

### System requirements
- Python 3.13;
- Docker (20.10+) with docker compose;
- [uv](https://docs.astral.sh/uv/).

### Tech stack
[![Python][Python-badge]][Python-url]
[![FastAPI][FastAPI-badge]][FastAPI-url]
[![Aiogram][Aiogram-badge]][Aiogram-url]
[![Postgres][Postgres-badge]][Postgres-url]
[![SQLAlchemy][SQLAlchemy-badge]][SQLAlchemy-url]
[![Docker][Docker-badge]][Docker-url]
[![Redis][Redis-badge]][Redis-url]
[![uv][uv-badge]][uv-url]

## Installation and start

<details>
<summary>
Local run (Docker + local services)
</summary>
<br>

1. Clone the repo and change directory to it:

```shell
git clone https://github.com/melax08/cheapskate.git && cd cheapskate
```

2. Create an `.env` file in the `src` directory and add the necessary environment variables to it (check `src/.env.example` for necessary variables.)
```shell
cp src/.env.example src/.env
```
```shell
vi src/.env
```

3. Install dependencies via `uv`:

```shell
uv sync
```

4. Run database and caching server via docker compose:

```shell
docker compose up -d
```

5. Change directory to the application source directory:

```shell
cd src
```

6. Apply database migrations and initial instances:

```shell
uv run alembic -c backend/alembic.ini upgrade head
uv run python3 -m backend.db_init
```


7. Run a bot and an API in the different terminal tabs:

```shell
# First tab
uv run fastapi dev api.py
```

```shell
# Second tab
uv run python3 -m bot
```

</details>

<details>
<summary>
Production run (Docker)
</summary>
<br>

1. Clone the repo and change directory to it:

```shell
git clone https://github.com/melax08/cheapskate.git && cd cheapskate
```

2. Create an `.env` file in the `src` directory and add the necessary environment variables to it (check `src/.env.example` for necessary variables.)
```shell
cp src/.env.example src/.env
```
```shell
vi src/.env
```

3. Run `docker compose` to create docker containers and run services:
```shell
docker compose -f infra/docker-compose-prod.yml up -d
```

</details>

## Settings and documentation

### Settings

Bot constants available in directory: `src/bot/constants/`

API constants and some bot constants you can configure in `.env` file (see example in `src/.env.example` file).

Common constants for bot and API you can find in `src/configs/constants.py`.

### Telegram commands and usage

Only Telegram users whose IDs are listed in the `ALLOWED_TELEGRAM_IDS` (check the `.env.example` file for details) environment variable have access to the bot. If there is no ID in this environment variable, then all users have access to the bot (not recommended).

<details>
<summary>
Create categories and expense management
</summary>
<br>

First, you need to create spending categories so that you can add expenses to them in the future.

To do this, send the `/add_category` command to the bot and follow the instructions.

![add_category.png](readme_files/example_screens/add_category.png)

Once at least one category has been created, you can add expenses. To do this, send the bot the amount of money that was spent, and then select the category to which the spending belongs.

![add_expense.png](readme_files/example_screens/add_expense.png)

![added_expense.png](readme_files/example_screens/added_expense.png)

If an expense was added by mistake, or the wrong category was selected, you can click on the delete expense button.

![delete_expense.png](readme_files/example_screens/delete_expense.png)

</details>

<details>
<summary>
Obtaining spending statistics
</summary>
<br>

There are several commands that allow you to get a variety of spending statistics.

`/money_left` - shows statistics on spending for the current month, including statistics on spending categories and the balance of funds until the end of the month.

![money_left.png](readme_files/example_screens/money_left.png)

`/today` - shows the amount of money spent today, including information by spending category

![today.png](readme_files/example_screens/today.png)

`/statistics` - allows you to view spending statistics for a specific month of a specific year.

![statistic_choose.png](readme_files/example_screens/statistic_choose.png)

![statistic_chosen.png](readme_files/example_screens/statistic_chosen.png)

</details>

### API documentation

If you run API locally by using `uvicorn`, you can get access to the swagger documentation of the API.

If you run API by command (before run this command, you need to install virtual environment for python3 and needed dependencies):

```shell
cd cheapskate/src && uvicorn api:app
```

Documentation will be available on URL: http://127.0.0.1:8000/docs

### For developers

Before starting development and creating new commits, apply git hooks by running the command:

```shell
pre-commit install
```

Now, when creating a new commit, the following will be automatically launched:

- [Ruff linter](https://docs.astral.sh/ruff/linter/);
- [Ruff formatter](https://docs.astral.sh/ruff/formatter/);
- [Pytest](https://docs.pytest.org/en/8.0.x/);
- [check-yaml, end-of-file-fixer, trailing-whitespace](https://github.com/pre-commit/pre-commit-hooks).

You can manage the pre-commit hooks in a file: `.pre-commit-config.yaml`


<!-- MARKDOWN LINKS & BADGES -->
[Python-url]: https://www.python.org/
[Python-badge]: https://img.shields.io/badge/Python-376f9f?style=for-the-badge&logo=python&logoColor=white
[Aiogram-url]: https://aiogram.dev/
[Poetry-url]: https://python-poetry.org
[Poetry-badge]: https://img.shields.io/badge/poetry-blue?style=for-the-badge&logo=Poetry&logoColor=white&link=https%3A%2F%2Fpython-poetry.org
[Aiogram-badge]: https://img.shields.io/badge/Aiogram-blue?style=for-the-badge
[Postgres-url]: https://www.postgresql.org/
[Postgres-badge]: https://img.shields.io/badge/postgres-306189?style=for-the-badge&logo=postgresql&logoColor=white
[SQLAlchemy-url]: https://www.sqlalchemy.org
[SQLAlchemy-badge]: https://img.shields.io/badge/sql-alchemy-red?style=for-the-badge
[FastAPI-url]: https://fastapi.tiangolo.com
[FastAPI-badge]: https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi
[Docker-url]: https://www.docker.com
[Docker-badge]: https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white
[Redis-badge]: https://img.shields.io/badge/redis-%23DD0031.svg?style=for-the-badge&logo=redis&logoColor=white
[Redis-url]: https://redis.io/
[uv-badge]: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json
[uv-url]: https://docs.astral.sh/uv/
