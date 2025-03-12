from os.path import join
from sys import argv

PROJECT_ROOT_PATH = None


def _get_template_content(template_path):
    """
    Get content of template Jenkinsfile.

    :return: Template Jenkinsfile content
    """
    with open(
        join(PROJECT_ROOT_PATH, template_path), mode="r", encoding="utf-8"
    ) as template:
        return template.readlines()


def _get_injection_index(pattern, jenkinsfile_content):
    """
    Get index of template code injection by finding 'stages' line number in main Jenkinsfile.

    :param jenkinsfile_content: Main Jenkinsfile content
    :return: Index of template code injection
    """
    return_value = 0
    for index, line in enumerate(jenkinsfile_content):
        if pattern in line:
            return_value = index
            break
    return return_value


def generate_test_jenkinsfile():
    """
    Generate TestJenkinsfile by injecting template code in line provided by _get_injection_index function.

    :return: None
    """
    with open(
        join(PROJECT_ROOT_PATH, "Jenkinsfile"), mode="r", encoding="utf-8"
    ) as main_jenkinsfile:
        jenkinsfile_content = main_jenkinsfile.readlines()
        jenkinsfile_content.insert(
            _get_injection_index("environment {", jenkinsfile_content),
            "".join(
                _get_template_content("tools/resources/TestPipelineParametersTemplate")
            ),
        )
    with open(
        join(PROJECT_ROOT_PATH, "tools/jenkins/ParametrizedTestJenkinsfile"),
        mode="w",
        encoding="utf-8",
    ) as test_jenkinsfile:
        test_jenkinsfile.writelines(jenkinsfile_content)


if __name__ == "__main__":
    PROJECT_ROOT_PATH = argv[1]
    generate_test_jenkinsfile()
    print("Generated tools/jenkins/ParametrizedTestJenkinsfile")
