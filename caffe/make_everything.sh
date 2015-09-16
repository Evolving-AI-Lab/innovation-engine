#!/bin/bash
make all -j 16 && make test -j 16 && make pycaffe -j 16
