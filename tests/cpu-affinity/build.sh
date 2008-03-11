#! /bin/sh
cd $(dirname $0) &&
g++ -o cpus cpus.cpp -pthread &&
./cpus
