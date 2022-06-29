. ./deploy/version.sh

docker stop $(docker ps -q --filter ancestor=$APP_NAME:$APP_VERSION)
docker rm $(docker ps -a -q --filter ancestor=$APP_NAME:$APP_VERSION)
docker rmi -f $APP_NAME:$APP_VERSION
docker build -f Dockerfile.production --tag $APP_NAME:$APP_VERSION .
docker run --name $APP_NAME -d $APP_NAME:$APP_VERSION
