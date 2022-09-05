echo "stop all containers .."
docker stop $(docker ps -a -q)
echo "remove all containers .."
docker rm $(docker ps -a -q)