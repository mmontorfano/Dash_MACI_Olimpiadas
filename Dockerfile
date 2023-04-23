FROM python:3.10
RUN pip install gunicorn
COPY ./pyproject.toml /app/pyproject.toml
WORKDIR /app
RUN pip install .
COPY . /app
EXPOSE 5000
CMD ["gunicorn", "--bind",  "0.0.0.0:5000", "dashboard.app:server"]
