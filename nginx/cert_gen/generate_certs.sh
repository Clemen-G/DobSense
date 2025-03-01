#!/usr/bin/env bash


# exit on any failure
set -e

CA_CERT_PATH=$1
APP_CERT_PATH=$2
APP_KEY_PATH=$3

if [ -z "$CA_CERT_PATH" ] || [ -z "$APP_CERT_PATH" ] || [ -z "$APP_KEY_PATH" ]; then
  echo "Usage: $0 <ca_cert_path> <app_cert_path> <app_key_path>"
  exit 1
fi

# Get the script's directory
SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)

# 0. Initialize working directory

TMP_DIR=$(mktemp -d)

# Set up a trap to clean up the temporary directory on exit
clean_up() {
  echo "Cleaning up"
  if [ -n "$TMP_DIR" ]; then
    rm -rf $TMP_DIR
  fi
}

trap clean_up EXIT

cd $TMP_DIR || exit 1
mkdir ca_files
touch ca_files/index.txt
echo '01' > ca_files/serial.txt

# 1. Generate CA self-signed certificate and private key

# Generate an in-memory random passphrase for the CA private key
# It will be discarded after the certificates are generated
# so that the root CA installed on the phone won't be misused.
export CA_PRIV_KEY_PASSPHRASE=$(openssl rand -base64 16)

echo "Generating CA certificate and private key"

openssl req -x509 \
-batch \
-quiet \
-newkey rsa:2048 \
-config $SCRIPT_DIR/openssl-ca.conf \
-days 825 \
-sha256 \
-passout env:CA_PRIV_KEY_PASSPHRASE \
-keyout ca_key.pem \
-out ca_cert.pem \
-outform PEM

# 2. Generate a private key and a certificate signing request for the application

echo "Generating app certificate signing request"

openssl req \
-config $SCRIPT_DIR/openssl-app.conf \
-batch \
-quiet \
-newkey rsa:2048 \
-sha256 \
-nodes \
-out app_cert_req.csr \
-keyout app_key.pem \
-outform PEM

# 3. Sign the app certificate request

echo "Signing app certificate"

openssl ca \
-batch \
-config $SCRIPT_DIR/openssl-ca.conf \
-policy signing_policy \
-extensions signing_req \
-passin env:CA_PRIV_KEY_PASSPHRASE \
-out app_cert.pem \
-infiles app_cert_req.csr

# Gets rid of the human-readable version of the certificate
openssl x509 -in app_cert.pem -out app_cert.pem

# 4. Deploy the certificate chain

echo "Deploying certificates"

cp app_cert.pem $APP_CERT_PATH
cat ca_cert.pem >> $APP_CERT_PATH
cp app_key.pem $APP_KEY_PATH

cp ca_cert.pem $CA_CERT_PATH

echo "Certificates generated successfully"