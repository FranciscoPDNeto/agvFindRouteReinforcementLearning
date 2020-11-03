#!/bin/bash

inputFilename=$1
learningRate=$2
explorationStrategyFactor=$3
discountFactor=$4
iterations=$5

python3 src/qlearning.py $inputFilename $learningRate $explorationStrategyFactor $discountFactor $iterations