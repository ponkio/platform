#!/bin/bash
sops -e --encrypted-regex '^(secrets)$' values.yaml > values.enc.yaml
