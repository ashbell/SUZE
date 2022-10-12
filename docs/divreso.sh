#!/bin/bash

cd $1

## check resolution
for i in `ls *.mp4`; do 
 resolutionDirty=`ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=s=x:p=0 $i`;
 resolution=`echo $resolutionDirty |  sed 's/\$//g' |sed 's/\r//g'`
 if [ -d ./$resolution/ ]; then
	 echo "alread exists!!!!!"
	 mv -v $i ./$resolution/$i
 else
	 mkdir $resolution
	 mv -v $i ./$resolution/$i
 fi
 echo "$i=$resolution" >>../res
 echo "----------------------- $i=$resolution" 
done;

