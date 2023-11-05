docker build -f Dockerfile -t mg_project2 .
docker tag mg_project2:latest 406097215781.dkr.ecr.us-west-1.amazonaws.com/mg_project2:latest
docker push 406097215781.dkr.ecr.us-west-1.amazonaws.com/mg_project2:latest