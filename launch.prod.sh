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
perl $SCRIPT_DIR/nginx/gen_nginx_conf.pl $dev_mode $dns_server > $SCRIPT_DIR/nginx/nginx.conf

if [ ! -f "/shared/tls/ca_cert.pem" ] || [ ! -f "/shared/tls/app_cert_chain.pem" ] || [ ! -f "/shared/tls/app_key.pem" ]; then
    echo "Generating certificates"
    mkdir -p /shared/tls
    $SCRIPT_DIR/nginx/cert_gen/generate_certs.sh /shared/tls/ca_cert.pem /shared/tls/app_cert_chain.pem /shared/tls/app_key.pem
fi

echo starting nginx
nginx -c $SCRIPT_DIR/nginx/nginx.conf || exit 1

cd $SCRIPT_DIR/backend && pipenv run python ./app/main.py --debug &
TORNADO_PID=$!
echo started tornado server with pid: $TORNADO_PID
    
wait $TORNADO_PID
