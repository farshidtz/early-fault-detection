#!/bin/bash
file=smtline-161127-0.05fr
chunksize=10737418240
for (( ; ; ))
do
	actualsize=$(wc -c <"$file".txt)
	if [ $actualsize -ge $chunksize ]; then
		echo size is over $chunksize bytes
		name=$file
		if [[ -e $name.txt ]] ; then
			i=0
			while [[ -e $name\_$i.txt ]] ; do
				let i++
			done
			name=$name\_$i
		fi
		echo "$name".txt
		mv "$file".txt "$name".txt
	fi
	sleep 60s
done

