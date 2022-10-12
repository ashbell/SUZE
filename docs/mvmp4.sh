#!/bin/bash

cd  $1
echo `pwd`
echo 'Working at -------: ' `pwd` >> /cygdrive/e/log
## 如果目标文件已经存在，要怎么处理？
n=1; 
for i in `find . -name \* |grep mp4`; 
	do  
		new=`printf %04d $n`;
		newfile=../mp4/$new.mp4
		if [ -f "$newfile" ]
		  then
			  newfile=../mp4/$RANDOM$RANDOM.mp4
		fi	
		mv -vn  $i    $newfile; 
		let n=n+1; 
	done;
rm -rvf  ./*
mkdir  ../mp4/A/  ../mp4/B/ ../mp4/C/  ../mp4/D/
##read p


