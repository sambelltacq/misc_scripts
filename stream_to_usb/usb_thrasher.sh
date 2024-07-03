#!/usr/bin/env sh

runtime=${1:-3600}
disknum=${2:-1}

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
    echo -e "\nLoop ${counter}" >> /mnt/scripts/thrash.log
    ./usb_handler.py --format=vfat ${disknum}
    ./usb_handler.py --mount ${disknum}
    ./usb_handler.py --stream --secs=${runtime} --concat=100 --filesdir=10000 ${disknum}
    sleep 1
    ls /media/disk_${disknum}/*/* | ./isramp -m${nchan} -c${spad0} -v1 -N1 | tee -a "/mnt/scripts/thrash.log"
    echo "exit here"
    sleep 5
    df -h /media/disk_${disknum} >> /mnt/scripts/thrash.log
    rm /media/disk_${disknum}/* -rf
    sleep 1
    df -h /media/disk_${disknum} >> /mnt/scripts/thrash.log

    echo "Complete" >> /mnt/scripts/thrash.log
    ./usb_handler.py --unmount ${disknum}
    counter=$((counter + 1))
done

