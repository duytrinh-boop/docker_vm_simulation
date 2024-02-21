#!/bin/sh

# check for command line args
if [ $1 ]
then
  echo "$1 hour"
  screen /opt/setup/admin/screen_component_sleep_datagen.sh $1
else
  echo "must pass number of hours. eg $0 2 - sleeps for 2 hours before spawing"
  exit 1
fi


