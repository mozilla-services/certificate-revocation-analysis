This collection of tools is designed to assemble a cascading
bloom filter containing all TLS certificate revocations, as described
in this [CRLite paper.](http://www.ccs.neu.edu/home/cbw/static/pdf/larisch-oakland17.pdf)

These tools were built from scratch, using the original CRLite research code as a design reference and closely following the documentation in their paper. 

## Dependancies
1. Python 3
2. Aria2c (or wget or Curl)
3. pyopenssl (at least version 16.1.0)
4. Lots of patience, as many of the scripts take several hours even with multiprocessing

## Instructions
### Part A: Obtaining all Certificates
Use `ct-fetch` from [`ct-mapreduce`](https://github.com/jcjones/ct-mapreduce)
to fetch all certificates from CT logs.

### Part B: Determining CRL Revocations
1. `cd get_CRL_revocations`
2. Edit `settings.py` `CT_FETCH_DATA_DIR` to point to the directory where you
   fetched the CT data in Part A.
3. `python extract_crls.py` This script will output 2 files:
   * `certs_using_crl.json` - all certificates which have listed CRLs
   * `CRL_servers` - all CRL distribution points
4. `aria2c -d all_CRLs -i CRL_servers -j 16`.
5. `python build_megaCRL.py`
6. `python build_CRL_revoked.py`.
7. `cat revokedCRLCerts/certs* > ../final_CRL_revoked.json`

### Part D: Building The Filter
0. Set `build_filter` as the working directory. This folder contains all scripts for Part D.
Make subdirectories `final_unrevoked` and `final_revoked`.

1. Use `python build_final_sets.py` to convert the data created from the steps above into a single
set of all revoked certificates and all valid certificates. This script uses multiprocessing,
so after running the script you will need to use `cat final_unrevoked/*.json > ../final_unrevoked.json`
and `cat final_revoked/*.json > ../final_revoked.json` to combine the results of the individual
workers into a single file. You can see how your results match against mine by comparing
against [this file](https://drive.google.com/file/d/0B_ImpEaqYaA8eHVlTnJ4cW9lclk/view?usp=sharing).

2. Use the command `node ./build_filer.js --max_old_space_size=32768 > filter` to assemble
the final filter. Be sure to change the `REVOKED` and `UNREVOKED` constants to reflect
accurately. **(acknowledgements to James Larisch for the build_filter.js code)**

## Acknowledgements 
Thanks to Eric Rescorla, J.C. Jones, James Larisch, the CRLite research team and the Mozilla Cryptography Engineering team.
