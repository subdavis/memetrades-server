#!/bin/bash
docker rm memect && docker rmi memes
docker build -f Dockerfile.web -t memes . 
docker run \ 
	-e "VIRTUAL_HOST=memetrades.com" \  
	-e "LETSENCRYPT_HOST=memetrades.com" \ 
	-e "LETSENCRYPT_EMAIL=developers@memetrades.com" \ 
	-dt -v /certs:/certs:rw --link mongo:mongo --name memect memes