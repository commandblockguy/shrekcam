docker stop /bodypix
docker rm /bodypix
docker build -t bodypix ./bodypix
docker run -d --name=bodypix -p 9000:9000 --gpus=all --shm-size=1g --ulimit memlock=-1 --ulimit stack=67108864 bodypix
