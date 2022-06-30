# version
. ./deploy/version.sh

# down
docker stop $(docker ps -q --filter ancestor=$APP_NAME:$APP_VERSION)
docker rm $(docker ps -a -q --filter ancestor=$APP_NAME:$APP_VERSION)
docker rmi -f $APP_NAME:$APP_VERSION
