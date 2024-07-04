#!/usr/bin/env sh

runtime=${1:-3600}
disknum=${2:-1}
max_runs=${2:-99999999}

logfile="/mnt/thrash.log"

set.site 0 sync_role master 125000
set.site 0 spad 1,8,0
run0 1 1,8,0

nchan=$(get.site 0 NCHAN)
spadlen=$(echo $(get.site 0 spad) | awk -F ',' '{print $2}')
spad0=$((nchan - spadlen))
echo "nchan ${nchan}"
echo "spadlen ${spadlen}"
echo "spad0 ${spad0}"

counter=0
while true; do
    echo -e "\nLoop ${counter}" >> $logfile

    ./usb_handler.py --mount ${disknum}
    ./usb_handler.py --stream --secs=${runtime} --concat=100 --filesdir=10000 ${disknum}
    sleep 1
    
    echo "isramp running"
    ls /media/disk_${disknum}/????/* | ./isramp -m${nchan} -c${spad0} -v1 -N1 | tee -a $logfile
    echo "isramp complete"
    sleep 5

    df -h /media/disk_${disknum} >> $logfile
    rm /media/disk_${disknum}/* -rf
    sleep 1

    echo "Complete" >> $logfile
    ./usb_handler.py --unmount ${disknum}

    ./usb_handler.py --format=vfat ${disknum} #format needed if disk become corrupted after repeated runs
    counter=$((counter + 1))
    if [ "$counter" -gt "$max_runs" ]; then
        break
    fi
done

