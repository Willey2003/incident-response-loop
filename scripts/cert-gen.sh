#!/bin/bash
# AegisForge Certificate Generation Script
# Generates TLS certificates for local development and testing

set -euo pipefail

CERT_DIR="${CERT_DIR:-./certs}"
DOMAIN="${DOMAIN:-aegisforge.example.com}"
DAYS="${DAYS:-365}"
CA_DAYS="${CA_DAYS:-730}"

mkdir -p "${CERT_DIR}"

generate_ca() {
    echo "Generating CA certificate..."
    openssl req -x509 -newkey rsa:4096 -sha256 -days "${CA_DAYS}" \
        -nodes -keyout "${CERT_DIR}/ca.key" -out "${CERT_DIR}/ca.crt" \
        -subj "/CN=AegisForge CA/O=AegisForge/OU=Security" \
        -addext "basicConstraints=critical,CA:TRUE" \
        -addext "keyUsage=critical,keyCertSign,cRLSign"
    
    chmod 600 "${CERT_DIR}/ca.key"
    echo "CA certificate generated: ${CERT_DIR}/ca.crt"
}

generate_server_cert() {
    local domain=$1
    local san="${2:-}"
    
    echo "Generating server certificate for ${domain}..."
    
    # Generate private key
    openssl genrsa -out "${CERT_DIR}/${domain}.key" 2048
    chmod 600 "${CERT_DIR}/${domain}.key"
    
    # Generate CSR
    local san_config=""
    if [[ -n "${san}" ]]; then
        san_config="[SAN]\nsubjectAltName=${san}"
    fi
    
    openssl req -new -key "${CERT_DIR}/${domain}.key" -out "${CERT_DIR}/${domain}.csr" \
        -subj "/CN=${domain}/O=AegisForge/OU=Security" \
        -addext "subjectAltName=${san:-DNS:${domain},DNS:*.${domain}}" \
        -addext "keyUsage=digitalSignature,keyEncipherment" \
        -addext "extendedKeyUsage=serverAuth,clientAuth"
    
    # Sign with CA
    local san_section=""
    if [[ -n "${san}" ]]; then
        san_section="subjectAltName=${san}"
    else
        san_section="subjectAltName=DNS:${domain},DNS:*.${domain}"
    fi
    
    openssl x509 -req -in "${CERT_DIR}/${domain}.csr" \
        -CA "${CERT_DIR}/ca.crt" -CAkey "${CERT_DIR}/ca.key" -CAcreateserial \
        -out "${CERT_DIR}/${domain}.crt" -days 365 -sha256 \
        -extensions SAN -extfile <(cat <<EOF
[SAN]
${san_section}
EOF
    )
    
    chmod 644 "${CERT_DIR}/${domain}.crt"
    echo "Server certificate generated: ${CERT_DIR}/${domain}.crt"
}

generate_client_cert() {
    local name=$1
    local org=$2
    
    echo "Generating client certificate for ${name}..."
    
    openssl genrsa -out "${CERT_DIR}/${name}.key" 2048
    chmod 600 "${CERT_DIR}/${name}.key"
    
    openssl req -new -key "${CERT_DIR}/${name}.key" -out "${CERT_DIR}/${name}.csr" \
        -subj "/CN=${name}/O=${org}/OU=Security"
    
    openssl x509 -req -in "${CERT_DIR}/${name}.csr" \
        -CA "${CERT_DIR}/ca.crt" -CAkey "${CERT_DIR}/ca.key" -CAcreateserial \
        -out "${CERT_DIR}/${name}.crt" -days 365 -sha256 \
        -extensions CLIENT -extfile <(cat <<EOF
[CLIENT]
keyUsage = digitalSignature, keyEncipherment
extendedKeyUsage = clientAuth
subjectAltName = email:${name}@example.com
EOF
    )
    
    chmod 644 "${CERT_DIR}/${name}.crt"
    echo "Client certificate generated: ${CERT_DIR}/${name}.crt"
}

create_k8s_secret() {
    local name=$1
    local namespace=$2
    
    echo "Creating Kubernetes TLS secret ${name} in namespace ${namespace}..."
    
    kubectl create secret tls "${name}" \
        --cert="${CERT_DIR}/${name}.crt" \
        --key="${CERT_DIR}/${name}.key" \
        --namespace="${namespace}" \
        --dry-run=client -o yaml | kubectl apply -f -
    
    echo "Secret ${name} created in namespace ${namespace}"
}

main() {
    local action="${1:-all}"
    
    case "${action}" in
        ca)
            generate_ca
            ;;
        server)
            generate_server_cert "${2:-aegisforge.example.com}" "${3:-}"
            ;;
        client)
            generate_client_cert "${2:-client}" "${4:-AegisForge}"
            ;;
        all)
            generate_ca
            generate_server_cert "aegisforge.example.com" "DNS:aegisforge.example.com,DNS:*.aegisforge.example.com,DNS:api.aegisforge.example.com,DNS:console.aegisforge.example.com"
            generate_server_cert "registry.local" "DNS:registry.local,DNS:*.registry.local"
            generate_client_cert "admin" "AegisForge"
            generate_client_cert "service-account" "AegisForge"
            ;;
        k8s)
            create_k8s_secret "aegisforge-tls" "aegisforge"
            create_k8s_secret "registry-tls" "aegisforge"
            create_k8s_secret "aegisforge-client" "aegisforge"
            ;;
        *)
            echo "Usage: $0 {ca|server|client|all|k8s} [domain] [san]"
            echo "  ca                     - Generate CA certificate"
            echo "  server <domain> [san]  - Generate server certificate"
            echo "  client <name> [org]    - Generate client certificate"
            echo "  all                    - Generate all certificates"
            echo "  k8s                    - Create Kubernetes secrets"
            exit 1
            ;;
    esac
}

main "$@"