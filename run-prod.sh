

docker-compose -f docker-compose.dev.yml rm -fs
docker-compose --env-file .prod.env -f docker-compose.dev.yml up --remove-orphans