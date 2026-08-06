FROM python:3.14.4
LABEL authors="Alex"

WORKDIR /code

RUN pip install --no-cache-dir poetry

COPY pyproject.toml poetry.lock ./

ENV PIP_DEFAULT_TIMEOUT=100
ENV POETRY_REQUESTS_TIMEOUT=60

RUN poetry config virtualenvs.create false && \
    poetry config repositories.pypi https://pypi.tuna.tsinghua.edu.cn/simple/ && \
    poetry install --no-interaction --no-ansi --no-root --only main --verbose

COPY . .

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]