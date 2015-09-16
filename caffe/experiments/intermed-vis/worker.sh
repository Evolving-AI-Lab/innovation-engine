#! /bin/bash 

# Run jobs based on work file

if [ "$1" = "" ]; then
    echo "Usage: $0 workfile"
    exit 1
fi

workfile="$1"
nargs=`head -n 1 "$workfile" | egrep -o '[0-9]+'`
cmd=`head -n 2 "$workfile" | tail -n 1 | sed -rn 's/#* *//p'`

if [ "$nargs" = "" -o "$cmd" = "" ]; then
    echo "Ill formed workfile"
    exit 1
fi




me=worker_`date +%y%m%d_%H%M%S_%N`

echo "[`datestamp -n`] $me starting."
echo "[`datestamp -n`] Command is \"$cmd\""

logdir=worker_logs

mkdir -p $logdir

#tmpdir=
#mkdir $tmpdir

while true; do
    # Unsafe non-locking bit
    sleep `rand`
    queuedline=`cat "$workfile" | grep '# queued' | head -n 1`
    #echo "queuedline is $queuedline"
    if [ "$queuedline" = "" ]; then break; fi

    jobcmd="$cmd"
    jobname=""
    for ii in `seq 1 $nargs`; do
        thisarg=$(echo $queuedline | gawk "{print \$$ii}")
        jobname+="_$thisarg"
        jobcmd=$(echo "$jobcmd" | sed "s/\$$ii/$thisarg/g")
    done
    jobname=$(echo "$jobname" | cut -c 2-)

    startat=`date +%y%m%d_%H%M%S`
    workingline=$(echo "$queuedline" | sed "s/queued/working $me $jobname $startat/")

    # Unsafe non-locking bit
    tmpfile=".tmp_`rand | cut -c 4-10`"
    cat $workfile | sed "s/$queuedline/$workingline/g" > $tmpfile
    if [ "`cat $workfile | wc -l`" != "`cat $tmpfile | wc -l`" ]; then
        echo "File error between $workfile and $tmpfile, quitting"
        exit 1
    fi
    mv $tmpfile $workfile

    echo "[`datestamp -n`] Starting job $jobname."

    echo " $jobcmd"   >"$logdir/$jobname.out"
    sh -c "$jobcmd"   >>"$logdir/$jobname.out" 2>"$logdir/$jobname.err"
    code="$?"

    endat=`date +%y%m%d_%H%M%S`
    doneline=$(echo "$workingline" | sed "s/working $me $jobname $startat/done $me $jobname $startat $endat $code/")

    # Unsafe non-locking bit
    sleep `rand`
    tmpfile=".tmp_`rand | cut -c 4-10`"
    cat $workfile | sed "s/$workingline/$doneline/g" > $tmpfile
    if [ "`cat $workfile | wc -l`" != "`cat $tmpfile | wc -l`" ]; then
        echo "File error between $workfile and $tmpfile, quitting"
        exit 1
    fi
    mv $tmpfile $workfile

    sleep 1

done

echo "[`datestamp -n`] No more jobs."
