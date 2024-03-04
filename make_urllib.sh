# /usr/bin/bash

docker run -v "$PWD":/var/task "lambci/lambda:build-python3.8" /bin/sh -c "pip install urllib3==1.26.15 -t python/lib/python3.8/site-packages/; exit"
zip -r urllib3-lambda.zip python 
sudo rm -rf python/
