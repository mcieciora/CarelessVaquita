from sys import executable  # pylint: disable=redefined-builtin
from glob import glob
import subprocess
from json import loads


def check_for_outdated_packages():
    """
    Verify if defined packages may be upgraded.

    Script compares list of outdated Python dependencies in current environment and the ones declared in all
    found requirements.txt files. It raises information about possibility to update specific packages, but does not
    require it.

    :return: None
    """
    outdated_dependencies_process_output = subprocess.check_output(
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
                    print(f"WARNING: Version of {name} declared in requirements file ({current_version}) is "
                          f"different than the one installed {outdated_dependencies[name]["version"]}")
                if name in outdated_dependencies and current_version != outdated_dependencies[name]["latest_version"]:
                    print(
                        f"WARNING: {name} is outdated. Consider upgrading from {current_version} to "
                        f"{outdated_dependencies[name]["latest_version"]}"
                    )
                    suggested_version = outdated_dependencies[name]['latest_version']
                output_req_file.append(f"{name}=={suggested_version}\n")

        with open(req_file, mode="w", encoding="utf-8") as req:
            req.writelines(output_req_file)


if __name__ == "__main__":
    check_for_outdated_packages()
