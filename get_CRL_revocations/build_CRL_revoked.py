import os
from multiprocessing import Process, Queue
import json
import sys

from settings import (
    CERTS_OUTFILE, COMBINED_CRL_OUTFILE,
    REVOKED_CERTS_DIR, REVOKED_CERTS_FILENAME_PREFIX
)

WORKERS = 16
OUTFILE = '%s/%s' % (REVOKED_CERTS_DIR, REVOKED_CERTS_FILENAME_PREFIX)


def doWork(i, megaCRL_org, megaCRL_CN):
    print('starting worker ' + str(i))
    with open(OUTFILE + str(i), 'w') as out:
        while True:
            try:
                cert_task = q.get()
                cert = json.loads(cert_task)
                serial = int(cert['serial_number'])
                issuer = cert['issuer']
            except:
                print("Error parsing/loading %s" % cert_task)
                continue  # skip to next certificate
            try:
                org = issuer['organization']
            except:
                org = 'unknown'
            try:
                CN = issuer['common_name']
            except:
                CN = 'unknown'
            if(isRevoked(megaCRL_org, megaCRL_CN, org, CN, serial)):
                out.write(json.dumps(cert) + '\n')


def isRevoked(megaCRL_org, megaCRL_CN, org, CN, serial):
    if org in megaCRL_org:
        if serial in megaCRL_org[org]:
            return True
    if CN in megaCRL_CN:
        if serial in megaCRL_CN[CN]:
            return True
    return False


def buildDict():
    megaCRL_CN = {}
    megaCRL_org = {}
    crlFile = open(COMBINED_CRL_OUTFILE, 'r')
    for line in crlFile:
        parsed = json.loads(line)
        issuer = parsed['crl_issuer']
        for entry in issuer:
            if entry[0] == "O":
                org = entry[1].replace(" ", "_")
                if org not in megaCRL_org:
                    megaCRL_org[org] = []
                for serial in parsed['cert_serials']:
                    megaCRL_org[org].append(int(serial, 16))
            if entry[0] == "CN":
                CN = entry[1].replace(" ", "_")
                if CN not in megaCRL_CN:
                    megaCRL_CN[CN] = []
                for serial in parsed['cert_serials']:
                    megaCRL_CN[CN].append(int(serial, 16))
    return megaCRL_CN, megaCRL_org


if __name__ == '__main__':
    print('Using %s and %s to create %s...' % (
        CERTS_OUTFILE, COMBINED_CRL_OUTFILE, REVOKED_CERTS_DIR
    ))
    if not os.path.exists(REVOKED_CERTS_DIR):
        os.makedirs(REVOKED_CERTS_DIR)
    megaCRL_CN, megaCRL_org = buildDict()
    q = Queue(WORKERS * 16)
    for i in range(WORKERS):
        p = Process(target=doWork, args=(i, megaCRL_org, megaCRL_CN, ))
        p.start()
    try:
        ctr = 0
        for cert in open(CERTS_OUTFILE, 'r'):
            q.put(cert)
            ctr += 1
            if(ctr % 10000 == 0):
                print(str(ctr) + " certificates processed")
    except KeyboardInterrupt:
        sys.exit(1)
