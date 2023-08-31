#!/bin/bash
TORNADO_PID=""
function trap_ctrlc ()
{
    nginx -s quit
    echo killing pid $TORNADO_PID
    kill -15 $TORNADO_PID
    # exit shell script with error code 2
    # if omitted, shell script will continue execution
    exit 2
}
 
trap "trap_ctrlc" 2

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
echo starting nginx
nginx -c $SCRIPT_DIR/nginx/nginx.conf

while true; do
    cd $SCRIPT_DIR/backend && pipenv run python ./app/main.py --debug &
    TORNADO_PID=$!
    echo starting tornado server with pid: $TORNADO_PID

    wait $TORNADO_PID
    sleep 5
done
