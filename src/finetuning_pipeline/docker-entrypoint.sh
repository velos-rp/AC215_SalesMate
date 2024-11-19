#!/bin/bash

echo "Container is running!!!"

args="$@"
echo $args

if [[ -z ${args} ]];
then
  echo "No command provided."
  exec /bin/bash
else
  $args
fi
