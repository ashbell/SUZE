#!/bin/bash
## merger  ./

cd $1
echo `pwd`

mp4_count=`ls ./ |grep mp4` 
if [ "$mp4_count" == '' ]; then
	find   . -name   *.ts  | xargs  -I {}  mv -vn {}  ./ts/ 
	cd ./ts/
	rm -rvf ./file
	rm  -rvf ./list

	ls *.ts | sort >> file
	for i in `cat ./file`; do echo "file  './$i' " >> list; done;
	ffmpeg -hide_banner -f concat  -safe 0 -i  ./list  -c copy ../output.mp4
	rm  -rvf ./file
	rm  -rvf ./list
else
	echo "File already combined"
fi
cd ..
##rm  -rvf  ./dirs*



