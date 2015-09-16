#! /bin/bash

function crop_montage_text() {
    size="$1"
    offset="$2"
    tile="$3"
    outname="$4"
    withtext="$5"   # set to non-empty to apply text

    tmpdir="tmp_`rand | cut -c 4-10`"
    mkdir $tmpdir

    echo "`pwd`: `ls *best_X.jpg`"
    for file in *best_X.jpg; do
        #picname=`printf 'cropped_%05d.png' $ii`

        # Faster
        convert $file -crop ${size}x${size}+${offset}+${offset} +repage $tmpdir/$file
    done

    montage $tmpdir/*.jpg -mode concatenate -background '#333' -tile $tile -geometry +1+1 $tmpdir/montage.jpg

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

here=`pwd`

# Reference
#    conv1   11  108
#    conv2   51   88
#    conv3   99   64
#    conv4  131   48
#    conv5  163   32
#    fc6    227    0
#    fc7    227    0
#    fc8    227    0

# conv1
#bigdir=results/150202_151620_6eaf854_priv_hp_search_0_conv1/conv1
#offsets="11 108"

# conv5
#bigdir=results/150202_152747_6eaf854_priv_hp_search_0_conv5/conv5
#offsets="163 32"

# fc8
#bigdir=results/150202_151936_6eaf854_priv_hp_search_0_fc8/fc8
#offsets="227 0"



# PAPER_ALL

# conv1
#littledir=conv1/conv1
#offsets="11 108"

# conv2
#littledir=conv2/conv2
#offsets="51 88"

# conv3
#littledir=conv3/conv3
#offsets="99 64"

# conv4
#littledir=conv4/conv4
#offsets="131 48"

# conv5
#littledir=conv5/conv5
#offsets="163 32"

# fc6
#littledir=fc6/fc6
#offsets="227 0"

# fc7
#littledir=fc7/fc7
#offsets="227 0"

# fc8
littledir=fc8/fc8
offsets="227 0"



bigdir=results/150203_212645_2468771_priv_paper_all/$littledir

for dir in `ls -d $bigdir/unit*/hs*`; do
#for dir in `ls -d $bigdir/unit*/hs* | head -n 1`; do
    echo $dir
    cd $dir
    crop_montage_text $offsets 3x3 montage.jpg        # not with text
    #crop_montage_text $offsets 3x3 montage.jpg withtext
    cd $here
done
