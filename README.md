# HOSPITAL KR API

This is simple map service for hospital search in Korea.

## DB Setup

Run Postgis:
```sh
docker run --name postgis-container \
  -e POSTGRES_USER=myuser \ # set user credentials
  -e POSTGRES_PASSWORD=mypassword \ # set user credentials
  -e POSTGRES_DB=mydb \ 
  -v $(pwd)/postgres-data:/var/lib/postgresql/data \
  -v $(pwd)/init-scripts:/docker-entrypoint-initdb.d \
  -p 5432:5432 \
  -d postgis/postgis
```

Stop Postgis:
```sh
docker rm -vf  postgis-container
```

Clear data:
```sh
sudo rm -rf postgres-data
```

## API Server

```sh
python main.py
```

## Test Frontend Web

```sh
python -m http.server 8080
```