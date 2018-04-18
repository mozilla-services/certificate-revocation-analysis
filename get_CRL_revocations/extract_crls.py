import json

from cryptography.x509.oid import NameOID

from ct_fetch_utils import processCTData
from settings import CT_FETCH_DATA_DIR, CRL_SERVERS_FILENAME, CERTS_OUTFILE


crl_outfile = open(CRL_SERVERS_FILENAME, "w")
cert_crl_outfile = open(CERTS_OUTFILE, "w")

certCounter = 0
INDICATOR = 1000
INDICATOR_STR = "thousand"


certs_list, CRL_distribution_points = processCTData(CT_FETCH_DATA_DIR)

print("processing certificates...")
for cert in certs_list:
    # print stats
    certCounter += 1
    if not(certCounter % INDICATOR):
        print(
            "%s %s certificates processed" %
            (certCounter / INDICATOR, INDICATOR_STR)
        )

    # get issuer and serial from cert
    try:
        org = cert.issuer.get_attributes_for_oid(
            NameOID.ORGANIZATION_NAME
        )[0].value.replace(" ", "_")
    except:
        org = 'unknown'
    try:
        cn = cert.issuer.get_attributes_for_oid(
            NameOID.COMMON_NAME
        )[0].value.replace(" ", "_")
    except:
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
        pass


print(
    "adding %s CRL distribution points to %s" %
    (len(CRL_distribution_points), CRL_SERVERS_FILENAME)
)
for distribution_point in CRL_distribution_points:
    crl_outfile.write(distribution_point + '\n')
