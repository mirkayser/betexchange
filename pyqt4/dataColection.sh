#!/bin/bash

#~ i="0"
#~ while [ $i -lt 2 ] ; do
echo 'starting data colection: ' $1
while ./render.py $1; do
      echo 'sleeping...'
      sleep 60
      #~ echo 'Starting Data Colection...'
      #~ i=$[$i+1]
      
done
#~ echo "Application has finished"
echo "event has finished: " $1
