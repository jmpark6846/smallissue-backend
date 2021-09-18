#!/bin/sh

sudo certbot -n -d smallissue.eba-4uzry5z8.ap-northeast-2.elasticbeanstalk.com --nginx --agree-tos --email jmpark6846@naver.com
sudo fuser -k 80/tcp