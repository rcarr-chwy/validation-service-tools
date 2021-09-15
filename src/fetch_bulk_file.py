import click
import pprint
import pandas as pd

import common.config as config
from common.MedPro.bulk import Bulk
from common.MedPro.utils import token_check


@click.command()
@click.option('-t',  '--token', help='File token',type=str)
@click.option('-o',  '--outfile', default="fetched.csv", help='Output filename', type=str)
@click.option('-v',  '--verbose', default="N", help='Verbose', type=str)
def bulk_fetch(token, outfile, verbose):
    bulk = Bulk(
        api_client_id=config.MEDPRO_API_CLIENT_ID,
        api_client_secret=config.MEDPRO_API_CLIENT_SECRET,
        auth_token=token_check(config.CLIENT_TOKEN_FILENAME,
                               config.MEDPRO_API_CLIENT_ID, 
                               config.MEDPRO_API_CLIENT_SECRET
                               )
    )

    final = []
    batchCount = 0
    batchTotal = 0
    totalRecords = 0
    p = bulk.statuses(filetype="")
    for i in p:
        if i['fileToken'] == token:
            # pprint.pprint(i)
            batchTotal = i['numberOfBatches']
            totalRecords = i['recordCount']

    fetchedRecords = 0
    while batchCount <= batchTotal:
        p = bulk.getProcessedFile(file_token=token, batch_number=batchCount)
        final.extend(p)
        if verbose.upper() == 'Y':
            print(batchCount, len(p))
        fetchedRecords += len(p)
        batchCount += 1

    if verbose.upper() == 'Y':
        print(f"Expected: {totalRecords}\nActual: {fetchedRecords}")

    transformedDataFrame =  pd.DataFrame(final)
    transformedDataFrame.to_csv(path_or_buf=outfile, index=False)


if __name__ == '__main__':
    bulk_fetch()
