import argparse
import json
import logging
from pathlib import Path
from tempfile import NamedTemporaryFile
import time

from nevermined_sdk_py import Config, Nevermined
from nevermined_sdk_py.nevermined.accounts import Account
from nevermined_sdk_py.nevermined.keeper import NeverminedKeeper as Keeper
from web3 import Web3


def run(args):
    logging.debug(f"script callef with args: {args}")

    # setup config
    options = {
        "keeper-contracts": {
            "keeper.url": args.node,
            "secret_store.url": args.secretstore_url,
        },
        "resources": {
            "downloads.path": args.path.as_posix(),
            "metadata.url": args.metadata_url,
            "gateway.url": args.gateway_url,
        },
    }
    config = Config(options_dict=options)
    logging.debug(f"nevermined config: {config}")

    # setup paths
    inputs_path = args.path / "inputs"
    inputs_path.mkdir()
    outputs_path = args.path / "outputs"
    outputs_path.mkdir()
    transformations_path = args.path / "transformations"
    transformations_path.mkdir()

    # setup nevermined
    nevermined = Nevermined(config)
    keeper = Keeper.get_instance()

    # setup consumer
    # here we need to create a temporary key file from the credentials
    key_file = NamedTemporaryFile("w", delete=False)
    json.dump(args.credentials, key_file)
    key_file.flush()
    key_file.close()
    consumer = Account(
        Web3.toChecksumAddress(args.credentials["address"]),
        password=args.password,
        key_file=key_file.name,
    )

    # resolve workflow
    workflow = nevermined.assets.resolve(args.workflow)
    logging.info(f"resolved workflow {args.workflow}")
    logging.debug(f"workflow ddo {workflow.as_dictionary()}")

    # get stages
    stages = workflow.get_service("metadata").main["workflow"]["stages"]
    logging.debug(f"stages {stages}")

    # get inputs and transformations
    inputs = []
    transformations = []
    for stage in stages:
        inputs += [input_["id"] for input_ in stage["input"]]
        if "transformation" in stage:
            transformations.append(stage["transformation"]["id"])
    logging.debug(f"inputs: {inputs}")
    logging.debug(f"transformations: {transformations}")

    # consume assets
    for did in inputs + transformations:
        ddo = nevermined.assets.resolve(did)
        service_agreement = ddo.get_service("access")

        if service_agreement:
            sa_id = None
            retry = 0
            while sa_id is None:
                try:
                    sa_id = nevermined.assets.order(did, service_agreement.index, consumer)
                except ValueError:
                    if retry == 3:
                        raise
                    logging.info(f"retrying ordering of the asset {did}")
                    retry += 1
                    time.sleep(30)
            logging.info(f"ordered asset {did} with service agreement {sa_id}")

            if ddo.metadata["main"]["type"] == "dataset":
                nevermined.assets.access(
                    sa_id,
                    did,
                    service_agreement.index,
                    consumer,
                    inputs_path.as_posix(),
                )
                logging.info(f"accessed asset {did}")
            elif ddo.metadata["main"]["type"] == "algorithm":
                nevermined.assets.access(
                    sa_id,
                    did,
                    service_agreement.index,
                    consumer,
                    transformations_path.as_posix(),
                )
                logging.info(f"accessed asset {did}")
        else:
            logging.warning(f"asset {did} contains no service of type `access`")

    return nevermined


def main():
    parser = argparse.ArgumentParser()
    group = parser.add_argument_group("required arguments")

    group.add_argument("-w", "--workflow", help="Workflow did", required=True)
    group.add_argument("-n", "--node", help="Node URL", required=True)
    group.add_argument("--gateway-url", help="Gateway URL", required=True)
    group.add_argument("--metadata-url", help="Metadata URL", required=True)
    group.add_argument("--secretstore-url", help="Secretstore URL", required=True)
    group.add_argument(
        "-c",
        "--credentials",
        help="Credentials password",
        type=json.loads,
        required=True,
    )
    group.add_argument("-p", "--password", help="Credentials password", required=True)
    group.add_argument("-l", "--path", help="Volume path", type=Path, required=True)
    parser.add_argument(
        "-v", "--verbose", help="Enables verbose mode", action="store_true"
    )
    args = parser.parse_args()

    # setup logging
    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="[%(asctime)s] [%(levelname)s] (%(name)s) %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    run(args)


if __name__ == "__main__":
    main()
