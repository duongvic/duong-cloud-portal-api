#!/bin/bash
source utils/color.sh
source utils/alias.sh

ROOT_DIR=`pwd`

echo "Building cas portal image"
cd ${ROOT_DIR}/deployment/dashboard
./build.sh
echo "------------END------------"

echo "Buildind cas webssh image"
cd ${ROOT_DIR}/deployment/webssh
./build.sh
echo "------------END------------"