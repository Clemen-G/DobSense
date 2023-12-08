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

echo generating nginx configuration
export dns_server=`grep -e '^nameserver ' /etc/resolv.conf | head -n 1 | tr -s ' ' | cut -d ' ' -f 2` 
export dev_mode=true
(cd $SCRIPT_DIR/backend && pipenv run python ../nginx/gen_nginx_conf.py ../nginx/nginx.conf.template > $SCRIPT_DIR/nginx/nginx.conf)

echo starting nginx
nginx -c $SCRIPT_DIR/nginx/nginx.conf || exit 1

# enables job control. required to use fg below
set -m

# !!! WARNING !!!
# I've broken this routine to simulate telescope movements via keyboard
# Last working version was at commit-id 38fd9ce
while true; do
    cd $SCRIPT_DIR/backend && pipenv run python ./app/main.py --debug &
    TORNADO_PID=$!
    echo starting tornado server with pid: $TORNADO_PID
    
    # wait $TORNADO_PID

    # needed to allow tornado to read from the keyboard
    fg
    sleep 5
done
