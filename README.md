This collection of tools is designed to assemble a cascading
bloom filter containing all TLS certificate revocations, as described
in this [CRLite paper.](http://www.ccs.neu.edu/home/cbw/static/pdf/larisch-oakland17.pdf)

These tools were built from scratch, using the original CRLite research code as a design reference and closely following the documentation in their paper. 

## Dependancies
1. `ct-fetch` from [`ct-mapreduce`](https://github.com/jcjones/ct-mapreduce)
1. Python 3
2. Aria2c
4. Patience; many scripts take several hours even with multiprocessing

## Instructions
### Part A: Obtaining all Certificates
Use `ct-fetch` from [`ct-mapreduce`](https://github.com/jcjones/ct-mapreduce)
to fetch all certificates from CT logs.

### Part B: Determining CRL Revocations
1. `pip install -r requirements.txt`
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

### Part C: Building The Filter
See https://github.com/mozilla-services/shavar-list-creation/pull/53


## Credits

* Benton Case for [the original
  code-base](https://github.com/casebenton/certificate-revocation-analysis)
* JC Jones for [`ct-mapreduce`](https://github.com/jcjones/ct-mapreduce)
* Mark Goodwin for original
  [`filter_cascade`](https://gist.githubusercontent.com/mozmark/c48275e9c07ccca3f8b530b88de6ecde/raw/19152f7f10925379420aa7721319a483273d867d/sample.py)
* The CRLite research team
