#!/bin/bash

# Remove .pem, .kubeconfig, csr.json and .csr files from the current and ansible directory
find . -maxdepth 2 -type f \( -name '*.pem' -o -name '*.kubeconfig' -o -name '*.csr' -o -name '*csr.json' \) ! -name 'kubernetes-key-pair.pem' -delete

echo "Files removed successfully."
