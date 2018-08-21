To use the package, call
```
python cli_linkage.py -r <data location> -t <workspace tag> -c <cut score> -b <block variables> -e <exact match variables> -s <string match variables> -m <match method>
```
Specific example:
```
python cli_linkage.py -r "records/data.0000.csv" -t "data" -c 6 -b SIN DOB -e StreetNumber Province City DOB SIN -s Name Street -m "jarowinkler"
```

You can also build the container with ```docker build```.
```
docker build ./ -t rl:v1
```
You can then run the container like so:
```
docker run -v ~/code/record-linkage:/tmp/rl rlkira:v1 python /tmp/rl/cli_linkage.py -r "tmp/rl/records/data.0000.csv" -t "data" -c 6 -b SIN DOB -e StreetNumber Province City DOB SIN -s Name Street -m "jarowinkler"
tmp/rl/records/data.0000.csv
```
This has the same result as the previous example with just the python interpreter.