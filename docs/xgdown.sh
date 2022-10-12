#!/bin/bash

echo $1 
echo "down to >>>>>>>>>>>>>>>>>>>>>>>>"
echo $2
cnt=$2

link=`echo $1 | sed  's/\r//g' |  sed 's/%OD\r//g'`
wget --no-check-certificate $link -O  $2

