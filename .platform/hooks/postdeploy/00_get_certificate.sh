#!/bin/sh

sudo docker stop `docker ps -q`
sudo certbot -n -d smallissue.app -d www.smallissue.app --expand --nginx --agree-tos --email jmpark6846@naver.com
sudo fuser -k 80/tcp
sudo docker start current_web_1
sudo docker start current_nginx_1