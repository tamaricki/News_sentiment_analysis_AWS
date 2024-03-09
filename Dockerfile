FROM python:3.8.6-buster

ENV PIP_DEFAULT_TIMEOUT=100 \
    PIP_NO_CACHE_DIR=1 

RUN pip3 install --upgrade pip && pip3 install poetry

COPY poetry.lock pyproject.toml ./
RUN poetry install

COPY . .
EXPOSE 8501
CMD poetry run streamlit run code/streamlitapp.py
