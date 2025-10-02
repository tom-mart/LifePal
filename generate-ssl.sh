#!/bin/bash

# Generate self-signed SSL certificates for local development

echo "Generating self-signed SSL certificates..."

# Create ssl directory if it doesn't exist
mkdir -p ssl

# Generate private key and certificate
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout ssl/localhost.key \
    -out ssl/localhost.crt \
    -subj "/C=US/ST=State/L=City/O=LifePal/OU=Dev/CN=localhost" \
    -addext "subjectAltName=DNS:localhost,DNS:*.lifepal.app,DNS:lifepal.app,IP:127.0.0.1,IP:192.168.1.229"

echo "SSL certificates generated successfully in ./ssl/"
echo "Certificate: ssl/localhost.crt"
echo "Private Key: ssl/localhost.key"
