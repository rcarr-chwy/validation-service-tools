import click
import pprint

import common.config as config
from common.MedPro.bulk import Bulk
from common.MedPro.utils import token_check


@click.command()
#@click.option('-v',  '--verbose', default='N', help='Show detailed progress',type=str)
def bulk_status():
    bulk = Bulk(
        api_client_id=config.MEDPRO_API_CLIENT_ID,
        api_client_secret=config.MEDPRO_API_CLIENT_SECRET,
        auth_token=token_check(config.CLIENT_TOKEN_FILENAME,
                               config.MEDPRO_API_CLIENT_ID, 
                               config.MEDPRO_API_CLIENT_SECRET
                               )
    )

    p = bulk.statuses(filetype="")
    for i in p:
        pprint.pprint(i)


if __name__ == '__main__':
    bulk_status()
