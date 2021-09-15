import csv
import click

import common.config as config
from common.MedPro.universe import Universe
from common.MedPro.utils import token_check
   

@click.command()
@click.option('--infile', default=None, help='CSV file to upload (MedProID, KyriosID).')
def processFile(infile):
    if infile is None:
        click.echo('You must supply an input file.')
        exit()

    # Read in Vets (MedproID, KyriosID)
    with open(infile) as f:
        reader = csv.reader(f)
        data = list(reader)

    universe = Universe(
        api_client_id=config.MEDPRO_API_CLIENT_ID,
        api_client_secret=config.MEDPRO_API_CLIENT_SECRET,
        auth_token=token_check(config.CLIENT_TOKEN_FILENAME, 
                               config.MEDPRO_API_CLIENT_ID, 
                               config.MEDPRO_API_CLIENT_SECRET
                               )
    )

    for item in data:
        if universe.inUniverse(medpro_id=item[0]) is False:
            payload = universe.addToUniverse(medpro_id=item[0], 
                                            client_id=item[1]
                                            )
            print(payload)

    print('Done.')


if __name__ == '__main__':
    processFile()
