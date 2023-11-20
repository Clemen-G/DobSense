#!/bin/bash
TORNADO_PID=""
function trap_signals ()
{
    echo caught termination signal
    echo killing nginx
    nginx -s quit
    echo killing tornado pid $TORNADO_PID
    kill -15 $TORNADO_PID
    # exit shell script with error code 2
    # if omitted, shell script will continue execution
    exit 2
}
trap "trap_signals" HUP INT QUIT TERM

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

export dev_mode=false

echo generating nginx configuration
export dns_server=`grep -e '^nameserver ' /etc/resolv.conf | head -n 1 | tr -s ' ' | cut -d ' ' -f 2` 
(cd $SCRIPT_DIR/backend && pipenv run python ../nginx/gen_nginx_conf.py ../nginx/nginx.conf.template > $SCRIPT_DIR/nginx/nginx.conf)

echo starting nginx
nginx -c $SCRIPT_DIR/nginx/nginx.conf || exit 1

cd $SCRIPT_DIR/backend && pipenv run python ./app/main.py --debug &
TORNADO_PID=$!
echo started tornado server with pid: $TORNADO_PID
    
wait $TORNADO_PID
