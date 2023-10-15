#!/bin/bash

# Remove .pem, .kubeconfig, csr.json and .csr files in the current directory
find . -maxdepth 1 -type f \( -name '*.pem' -o -name '*.kubeconfig' -o -name '*.csr' -o -name '*csr.json' \) ! -name 'kubernetes-key-pair.pem' -delete

echo "Files removed successfully."
