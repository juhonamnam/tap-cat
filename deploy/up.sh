# version
. ./deploy/version.sh

# down
. ./deploy/down.sh

# up
mkdir -p logs

docker build \
    -f Dockerfile.production \
    --tag $APP_NAME:$APP_VERSION .

docker run \
    --name $APP_NAME \
    -v $(pwd)/logs:/app/logs \
    -d $APP_NAME:$APP_VERSION production
