import click
import common.config as config

from common.MedPro.universe import Universe
from common.MedPro.utils import token_check
from common import utils
 
@click.command()
@click.option('-i',  '--medproid', required=True, help='Show detailed progress',type=str)
def check_universe(medproid: str):
    universe = Universe(
        api_client_id=config.MEDPRO_API_CLIENT_ID,
        api_client_secret=config.MEDPRO_API_CLIENT_SECRET,
        auth_token=token_check(config.CLIENT_TOKEN_FILENAME, 
                               config.MEDPRO_API_CLIENT_ID, 
                               config.MEDPRO_API_CLIENT_SECRET
                               )
    )

    print(universe.inUniverse(medpro_id=medproid))

if __name__ == '__main__':
    check_universe()
