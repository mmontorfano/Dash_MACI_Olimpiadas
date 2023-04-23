# dashboard-template

## Ejecuta tu aplicación en modo development

```sh
pip install .
python dashboard/app.py`
```

Luego podrás ir a tu navegador y entrar a http://localhost:5000

## Ejecuta tu aplicación con docker

``` sh
docker build -t mi-app .
docker run -p 5000:5000 mi-app
```

## Ejecuta tu aplicación con docker compose
Si tienes Docker Compose v2 usa el comando de compose v2

``` sh
docker compose up
```

Si tienes Docker Compose v1 usa el comando de compose v1

``` sh
docker-compose up
```