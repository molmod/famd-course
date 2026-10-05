#!/bin/bash

for file in $(git ls-files | grep 'ipynb$' | grep -v '^03'); do
  echo Running ${file}
  jupyter nbconvert ${file} --to notebook --execute --ExecutePreprocessor.timeout=-1
done
