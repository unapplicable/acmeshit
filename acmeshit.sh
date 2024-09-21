#!/usr/bin/bash
b=$(dirname $0)
exec env VIRTUAL_ENV=$b/env $b/env/bin/python3 $b/acmeshit.py $* 
