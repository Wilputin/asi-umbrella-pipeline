import asyncio
import logging
import pathlib

import yaml

from pipeline.configuration import PipelineConfiguration
from pipeline.pods import ApiApp, DataPuller, DataWriter, MetaIngestion

"""
for demonstration purposes this pipeline is designed as a monolith repo
please refer to the README.md at the root of the repository to learn about the
possible correct arcitecture

pipeline is ran in a single shot and query results trought the Api client is returned to the pod logs

"""

pipeline = {
    "meta_ingestion": MetaIngestion,
    "data_puller": DataPuller,
    "data_writer": DataWriter,
    "api_app": ApiApp,
}

root_repo_dir = pathlib.Path(__file__).parents[2]
config_source: pathlib.Path = root_repo_dir / "./configuration.yaml"

logger_map = {"info": logging.INFO, "debug": logging.DEBUG, "error": logging.ERROR}


def main():
    asyncio.run(_main())


def get_modules_to_run(config: PipelineConfiguration) -> dict:
    active_modules = {}
    for module in config.modules:
        if module.active:
            active_modules[module.name] = {
                "module": pipeline[module.name],
                "config": module.config,
            }
    return active_modules


async def _main():
    with open(config_source) as f:
        config = yaml.safe_load(f)
        pipeline_config = PipelineConfiguration(**config)
    active_modules = get_modules_to_run(pipeline_config)
    for package_name, module in active_modules.items():
        logger = logging.Logger(name=package_name)
        configuration = module["config"]
        logger.setLevel(logger_map[configuration.log_level])
        app = module["module"](logger=logger, config=configuration)
        await app.main()


if __name__ == "__main__":
    main()
