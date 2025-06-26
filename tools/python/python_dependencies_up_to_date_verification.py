from sys import executable
from glob import glob
from subprocess import check_output
from json import loads
from logging import getLogger


logger = getLogger(__name__)


def check_for_outdated_packages():
    """
    Verify if defined packages may be upgraded.

    Script compares list of outdated Python dependencies in current environment and the ones declared in all
    found requirements.txt files. It raises information about possibility to update specific packages, but does not
    require it.

    :return: None
    """
    outdated_dependencies_process_output = check_output(
        [executable, "-m", "pip", "list", "-o", "--format", "json"]
    )
    outdated_dependencies = {}
    for outdated_dependency in loads(outdated_dependencies_process_output):
        outdated_dependencies[outdated_dependency["name"]] = {
            "version": outdated_dependency["version"],
            "latest_version": outdated_dependency["latest_version"]
        }

    for req_file in glob("./requirements/**/requirements.txt"):
        with open(req_file, mode="r", encoding="utf-8") as req:
            all_file_reqs = [r for r in req.readlines()]
            output_req_file = []
            for dependency in all_file_reqs:
                name, current_version = dependency.replace("\n", "").split("==")

                suggested_version = current_version
                if name in outdated_dependencies and current_version != outdated_dependencies[name]["version"]:
                    logger.info("WARNING: Version of %s declared in requirements file (%s) is "
                                "different than the one installed %s", name, current_version,
                                outdated_dependencies[name]["version"])
                if name in outdated_dependencies and current_version != outdated_dependencies[name]["latest_version"]:
                    logger.info(
                        "WARNING: %s is outdated. Consider upgrading from %s to %s", name, current_version,
                        outdated_dependencies[name]["latest_version"])
                    suggested_version = outdated_dependencies[name]['latest_version']
                output_req_file.append(f"{name}=={suggested_version}\n")

        with open(req_file, mode="w", encoding="utf-8") as req:
            req.writelines(output_req_file)


if __name__ == "__main__":
    check_for_outdated_packages()
