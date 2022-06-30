#!/bin/sh

echo The script should be run on the repository\'s master/main branch

if [ $# -lt 1 ]; then
    echo Missing regex pattern
    exit 1
fi

regexSearchPattern=$1
logFile=~/gitscan.log

function swapBranch {
    git checkout $1 > /dev/null 2>&1
}

function searchFiles {
    grep -nri -E $regexSearchPattern . && (echo "Branch: $1, Commit ID: $2" >> $logFile)
}

echo "Running scan inside $(pwd) with pattern $regexSearchPattern" >> $logFile
date >> $logFile

# Initially at master/main branch
currentBranch=$(git rev-parse --abbrev-ref HEAD)
for commitId in $(git log --pretty=format:"%h"); do
    # Swap through every commit in git log
    swapBranch $commitId
    # And scan the current directory using grep
    searchFiles $currentBranch $commitId
done

# Then process every other branch
for branchFullName in $(git branch -r | grep -vE "HEAD|master"); do
    branchName=${branchFullName#*/}
    swapBranch $branchName
    for commitId in $(git log --pretty=format:"%h"); do
        swapBranch $commitId
        searchFiles $branchName $commitId
    done
done

# Change to original starting branch
swapBranch $currentBranch

echo "----" >> $logFile


