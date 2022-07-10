# env
if [[ -f ./.env ]]; then
    echo "getting environment variables from .env..."
    . ./.env
fi

# Stop Running Containers
RUNNING_CONTAINERS=$(docker ps -q --filter ancestor=$APP_NAME:$APP_VERSION)

if [ ${#RUNNING_CONTAINERS} -ne 0 ]; then
    echo "Stopping currently running containers..."
    docker stop $RUNNING_CONTAINERS
fi

# Delete Containers
ALL_CONTAINERS=$(docker ps -a -q --filter ancestor=$APP_NAME:$APP_VERSION)

if [ ${#ALL_CONTAINERS} -ne 0 ]; then
    echo "Deleting containers..."
    docker rm $ALL_CONTAINERS
fi

# Delete Image
docker rmi -f $APP_NAME:$APP_VERSION

# Up
mkdir -p logs

docker build \
    -f Dockerfile.production \
    --tag $APP_NAME:$APP_VERSION .

docker run \
    --name $APP_NAME \
    -e UPBIT_ACCESS_KEY=$UPBIT_ACCESS_KEY \
    -e UPBIT_SECRET_KEY=$UPBIT_SECRET_KEY \
    -e TELE_KEY=$TELE_KEY \
    -e TELE_USER_ID=$TELE_USER_ID \
    -v $(pwd)/logs:/app/logs \
    -d $APP_NAME:$APP_VERSION production
