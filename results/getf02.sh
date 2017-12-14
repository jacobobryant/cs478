#!/bin/bash
for f in ./subset_wrapperforward_10cv/j48.txt ./subset_wrapperforward_10cv/bayesnet.txt ./subset_wrapperforward_10cv/mlp.txt ./subset_wrapperforward_10cv/naivebayes.txt ./all_features/j48.txt ./all_features/bayesnet.txt ./all_features/mlp.txt ./all_features/naivebayes.txt ./subset_wrapperforward_training/j48.txt ./subset_wrapperforward_training/bayesnet.txt ./subset_wrapperforward_training/mlp.txt ./subset_wrapperforward_training/naivebayes.txt; do
    prec=$(tail $f | awk 'NR==1 {print $3}')
    rec=$(tail $f | awk 'NR==1 {print $4}')
    echo $f:
    python -c "print((1+0.2**2)*($prec * $rec)/(0.2**2 * $prec + $rec))"
    echo
done
