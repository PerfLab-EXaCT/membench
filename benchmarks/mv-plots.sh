#! /bin/bash

for d in result*/ ; do
    mkdir -p $d/plots/
    cp $d/*/*.png $d/plots
    echo "Plots for $d can be found at $d/plots"
done