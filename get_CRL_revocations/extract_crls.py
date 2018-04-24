from collections import Counter
import json

from cryptography.x509.oid import NameOID

from ct_fetch_utils import processCTData
from settings import CT_FETCH_DATA_DIR, CRL_SERVERS_FILENAME, CERTS_OUTFILE


crl_outfile = open(CRL_SERVERS_FILENAME, "w")
cert_crl_outfile = open(CERTS_OUTFILE, "w")

counter = Counter()
CERTS_INDICATOR = 10000
CRLS_INDICATOR = 1000


certs_list, CRL_distribution_points = processCTData(CT_FETCH_DATA_DIR)

print("processing certificates...")
for cert in certs_list:
    # print stats
    counter["Certs processed"] += 1
    if not(counter["Certs processed"] % CERTS_INDICATOR):
        print("Processing results: {}".format(counter))

    # get issuer and serial from cert
    try:
        org = cert.issuer.get_attributes_for_oid(
            NameOID.ORGANIZATION_NAME
        )[0].value.replace(" ", "_")
    except:
        counter["Unknown orgs"] += 1
        org = 'unknown'
    try:
        cn = cert.issuer.get_attributes_for_oid(
            NameOID.COMMON_NAME
        )[0].value.replace(" ", "_")
    except:
        counter["Unknown CN"] += 1
        cn = 'unknown'

    cert_for_json = {
        'serial_number': int(cert.serial_number),
        'issuer': {
            'organization': org,
            'common_name': cn
        }
    }

    try:
        cert_crl_outfile.write(json.dumps(cert_for_json) + '\n')
    except TypeError:
        # TODO: handle errors?
        counter["Cert writing errors"] += 1


print(
    "adding %s CRL distribution points to %s" %
    (len(CRL_distribution_points), CRL_SERVERS_FILENAME)
)
for distribution_point in CRL_distribution_points:
    try:
        crl_outfile.write(distribution_point + '\n')
        counter["CRLs written"] += 1
        if not(counter["CRLs written"] % CRLS_INDICATOR):
            print("Processing results: {}".format(counter))
    except TypeError as e:
        counter["CRL writing error"] += 1
        # print('TypeError writing CRL point to crl_outfile: %s' % e)

print("Processing results: {}".format(counter))
