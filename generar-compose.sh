#!/bin/bash
echo "Generando Yaml"
python3 docker-compose-generator.py $1 $2
echo "Yaml generado"