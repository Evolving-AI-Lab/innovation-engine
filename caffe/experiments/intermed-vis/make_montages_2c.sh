#! /bin/bash

function crop_montage_text() {
    size="$1"
    offset="$2"
    tile="$3"
    outname="$4"
    withtext="$5"   # set to non-empty to apply text

    # Check if it's already compiled
    if [ "`ls -rt *best_X.png montage.jpg | tail -n 1`" = "montage.jpg" ]; then
        echo "Skipping $outname; already up to date."
        return 0
    else
        echo "Do need to make $outname"
    fi
    #sleep 10

    tmpdir="tmp_`rand | cut -c 4-10`"
    mkdir $tmpdir

    echo "`pwd`: `ls *best_X.png`"
    for file in *best_X.png; do
        #picname=`printf 'cropped_%05d.png' $ii`

        # Faster
        convert $file -crop ${size}x${size}+${offset}+${offset} +repage $tmpdir/$file
    done

    montage $tmpdir/*.png -mode concatenate -background '#333' -tile $tile -geometry +1+1 $tmpdir/montage.jpg

    if [ "$withtext" != "" ]; then
        infofile=$(ls *info.txt | head -n 1)
        text=$(cat "$infofile" | egrep -v 'best_xx| ii|lastxx|std|x0' | sed 's/[[]/(/' | sed 's/[]]/)/')
        convert $tmpdir/montage.jpg -size 450x430 -append -gravity South -pointsize 12 label:"$text" -gravity South -append "$outname"
    else
        mv $tmpdir/montage.jpg "$outname"
    fi

    rm -rf $tmpdir
    #echo "Created $outname"
}

if [ "$1" = "" ]; then
    echo "Usage: $0 layer"
    exit 1
fi

layer="$1"

# Reference
#    conv1   11  108
#    conv2   51   88
#    conv3   99   64
#    conv4  131   48
#    conv5  163   32
#    fc6    227    0
#    fc7    227    0
#    fc8    227    0
case $layer in
    conv1 )
        offsets="11 108"
        ;;
    conv2 )
        offsets="51 88"
        ;;
    conv3 )
        offsets="99 64"
        ;;
    conv4 )
        offsets="131 48"
        ;;
    conv5 )
        offsets="163 32"
        ;;
    fc6|fc7|fc8|prob )
        offsets="227 0"
        ;;
    * )
        echo "Unknown layer $layer"
        exit 1
        ;;
esac


here=`pwd`

# PAPER_ALL

layerdir=results/150205-anh-cppn/$layer/$layer

for hsdir in `ls -d $layerdir/unit*/cppn`; do
#for dir in `ls -d $layerdir/unit*/hs* | head -n 1`; do
    echo $hsdir
    cd $hsdir
    crop_montage_text $offsets 3x3 montage.jpg        # not with text
    #crop_montage_text $offsets 3x3 montage.jpg withtext
    cd $here
done
