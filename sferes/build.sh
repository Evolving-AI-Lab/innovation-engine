#!/bin/bash
home=$(echo ~)

quit=0

# Remove the build folder
rm -rf ./build
echo "Build folder removed."

# Check the building folder, either on local or Moran
if [ "$home" == "/home/anh" ]
then    
    echo "Configuring sferes for local.."    
    echo "..."
    ./waf clean
    ./waf distclean
    #./waf configure --boost-include=/home/anh/src/local/include --boost-lib=/home/anh/src/local/lib --eigen3=/home/anh/src/local/include --mpi=/home/anh/openmpi
    ./waf configure --boost-include=/home/anh/src/local/include --boost-lib=/home/anh/src/local/lib --eigen3=/home/anh/src/local/include
    
    quit=1
    
else
  if [ "$home" == "/home/anguyen8" ]
  then 
      echo "Configuring sferes for Moran.."
      echo "..."
      ./waf clean
      ./waf distclean

      # TBB
      # ./waf configure --boost-include=/project/EvolvingAI/anguyen8/local/include/ --boost-libs=/project/EvolvingAI/anguyen8/local/lib/ --eigen3=/home/anguyen8/local/include --mpi=/apps/OPENMPI/gnu/4.8.2/1.6.5 --tbb=/home/anguyen8/local --libs=/home/anguyen8/local/lib
      
      # MPI (No TBB)
      #./waf configure --boost-include=/project/EvolvingAI/anguyen8/local/include/ --boost-libs=/project/EvolvingAI/anguyen8/local/lib/ --eigen3=/home/anguyen8/local/include --mpi=/apps/OPENMPI/gnu/4.8.2/1.6.5 --libs=/home/anguyen8/local/lib
      #./waf configure --boost-include=/project/EvolvingAI/anguyen8/local/include/ --boost-libs=/project/EvolvingAI/anguyen8/local/lib/ --eigen3=/home/anguyen8/local/include --mpi=/apps/OPENMPI/gnu/4.8.3/1.8.4 --libs=/home/anguyen8/local/lib --cpp11=yes
      ./waf configure --boost-include=/project/EvolvingAI/anguyen8/boost_1_57_0 --boost-libs=/project/EvolvingAI/anguyen8/boost_1_57_0/stage/lib --eigen3=/home/anguyen8/local/include --mpi=/apps/OPENMPI/gnu/4.8.3/1.8.4 --libs=/project/EvolvingAI/anguyen8/local/lib --includes=/project/EvolvingAI/anguyen8/local/include --cpp11=yes
      #./waf configure --boost-include=/home/anguyen8/local/include/ --boost-libs=/home/anguyen8/local/lib/ --eigen3=/home/anguyen8/local/include --mpi=/apps/OPENMPI/gnu/4.8.3/1.8.4 --libs=/project/EvolvingAI/anguyen8/local/lib --includes=/project/EvolvingAI/anguyen8/local/include --cpp11=yes
      
      quit=1

  else
    echo "Unknown environment. Building stopped."    
  fi
fi

if [ "$quit" -eq "1" ]
then
    echo "Building local.."    
    echo "..."
    echo "..."
    ./waf build
    
    echo "Building exp/images.."
    echo "..."
    echo "..."
    ./waf --exp images
fi

