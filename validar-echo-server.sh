#!/bin/bash
make docker-compose-up
docker build -t validator -f ./validator/Dockerfile .
MESSAGE="hola"
RESULT=$(docker run --rm --network tp0_testing_net validator sh -c "echo "$MESSAGE" | nc -v -w 2 server 12345")
if [ "$RESULT" = "$MESSAGE" ]; then
    echo "action: test_echo_server | result: success"
else
    echo "action: test_echo_server | result: fail"
fi
make docker-compose-down
docker rmi validator