#!/bin/bash
cd /Users/julietnwagwuume-ezeoke/_UILCode/gqe-phd/fpopt/studies2/msd2/static/_04_temp/workflow/outputs
echo "Summary of MSD2 outputs"

echo "Total:" && ls | wc -l

echo "Rotated:" && fd -p 'rotate/out.json' | wc -l

echo "Orthogonalized:" && fd -p 'ortho/out.json' | wc -l

echo "Simplified:" && fd -p 'simplify/out.json' | wc -l

echo "XMoved:" && fd -p 'xmove/out.json' | wc -l

echo "YMoved:" && fd -p 'ymove/out.json' | wc -l

# TODO function and saving in variables..
