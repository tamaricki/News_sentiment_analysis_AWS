# /usr/bin/bash
docker run -v "$PWD":/var/task "lambci/lambda:build-python3.8" /bin/sh -c "pip install newsapi-python psycopg2-binary==2.9.1 -t python/lib/python3.8/site-packages/; exit"
zip -r newsapi_psycopg.zip python 
sudo rm -rf python/
