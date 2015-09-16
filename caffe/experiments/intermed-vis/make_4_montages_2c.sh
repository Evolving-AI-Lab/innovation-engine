#! /bin/bash

if [ "$1" = "" ]; then
    echo "Usage: $0 layer"
    exit 1
fi

layer="$1"

bigdir=results/150203_212645_2468771_priv_paper_all/$layer/$layer
pushd $bigdir
echo

for unit in `\ls -d unit*`; do
    cd $unit
    outfile=${layer}_${unit}_montage.jpg

    if [ "`ls -rt {hs0081,hs0141,hs0275,hs0287}/montage.jpg $outfile | tail -n 1`" = "$outfile" ]; then
        echo "Skipping $outfile; already up to date."
    else
        echo "Do need to make $outfile"
        montage {hs0081,hs0141,hs0275,hs0287}/montage.jpg -mode concatenate -background '#333' -tile 2x2 -geometry +2+2 $outfile
        echo $outfile
        #sleep 10
    fi

    cd ..
done

echo
popd
