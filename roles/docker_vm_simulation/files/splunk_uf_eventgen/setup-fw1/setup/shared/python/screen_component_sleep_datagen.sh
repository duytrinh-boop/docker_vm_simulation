#!/bin/sh

# check for command line args
if [ $1 ]
then
  echo "$1 hour"
else
  echo "must pass number of hours. eg $0 2 - sleeps for 2 hours before spawing"
  exit 1
fi
# look for at least 1 running generator
l=$(ps aux  | grep generate_data.py | grep -v grep | awk '{ print $2 }' )
if echo $l | grep -q "[[:digit:]]"
then 
  echo "datagen running" 
else 
  echo "No datagen running"
fi
# kill all running generators
echo "stopping datagen"
for i in $l
do
  echo $i
  kill -9 $i
done
sleep 1
# convert arg to hours
hours=$(echo "60*60*$1" | bc)
echo "sleeping for $1 hours ($hours seconds)"
sleep $hours
# restart datagen
sudo screen /opt/setup/admin/generate_data.py
exit

