#!/bin/bash
cd /Users/julietnwagwuume-ezeoke/_UILCode/gqe-phd/fpopt/studies2/msd2/static/_04_temp/workflow/outputs
find . -mindepth 1 -maxdepth 1 -type d \
  -exec test -d "{}/ortho" \; \
  -a ! -exec test -d "{}/simplify" \; \
  -print
