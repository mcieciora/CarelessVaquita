def curDate = new Date().format("yyMMdd-HHmm", TimeZone.getTimeZone("UTC"))
Integer build_test_image

pipeline {
    agent {
        label "executor"
    }
    environment {
        FLAG = getValue("FLAG", "smoke")
        TEST_GROUPS = getValue("TEST_GROUP", "all")
        REGULAR_BUILD = getValue("REGULAR_BUILD", true)
        BRANCH_TO_USE = getValue("BRANCH", BRANCH_NAME)
        IS_NIGHTLY = getValue("IS_NIGHTLY", false)
        FORCE_DOCKER_IMAGE_BUILD = getValue("FORCE_BUILD", false)
    }
    options {
        skipDefaultCheckout()
    }
    stages {
        stage ("Checkout branch") {
            steps {
                script {
                    sh "curl -OL https://raw.githubusercontent.com/mcieciora/CarelessVaquita/refs/heads/${BRANCH_TO_USE}/.tools_config"
                    def BRANCH_REV = BRANCH_TO_USE.equals("develop") || BRANCH_TO_USE.equals("master") ? "HEAD^1" : "develop"
                    withEnv(getToolsConfig()) {
                        withCredentials([sshUserPrivateKey(credentialsId: "agent_${NODE_NAME}", keyFileVariable: "key")]) {
                            sh 'GIT_SSH_COMMAND="ssh -i $key"'
                            checkout scmGit(branches: [[name: "*/${BRANCH_TO_USE}"]], extensions: [], userRemoteConfigs: [[url: "${REPO_URL}"]])
                        }
                    }
                    currentBuild.description = "Branch: ${BRANCH_TO_USE}\nFlag: ${FLAG}\nGroups: ${TEST_GROUPS}"
                    build_test_image = sh(script: "git diff --name-only \$(git rev-parse HEAD) \$(git rev-parse origin/${BRANCH_REV}) | grep -e automated_tests -e src -e requirements -e tools/python",
                                          returnStatus: true)
                    build_merge_bot_image = sh(script: "git diff --name-only \$(git rev-parse HEAD) \$(git rev-parse origin/${BRANCH_REV}) | grep -e required_reviewers -e src -e requirements/merge_bot -e tools/python/merge_bot.py -e tools/merge_bot/Dockerfile",
                                          returnStatus: true)
                }
            }
        }
        stage ("Prepare docker images") {
            parallel {
                stage ("Build test image") {
                    when {
                        anyOf {
                            expression {build_test_image == 0}
                            expression {FORCE_DOCKER_IMAGE_BUILD.toBoolean() == true}
                        }
                    }
                    steps {
                        script {
                            withEnv(getToolsConfig()) {
                                sh "docker build --build-arg DEFAULT_IMAGE_TAG=${DEFAULT_IMAGE_TAG} --no-cache -t test_image -f automated_tests/Dockerfile ."
                                if (BRANCH_TO_USE == "master" || BRANCH_TO_USE == "develop") {
                                    sh "docker tag test_image ${DOCKERHUB_REPO}:test_image"
                                    withCredentials([usernamePassword(credentialsId: "dockerhub_id", usernameVariable: "USERNAME", passwordVariable: "PASSWORD")]) {
                                        sh "docker login --username $USERNAME --password $PASSWORD"
                                        sh "docker push ${DOCKERHUB_REPO}:test_image"
                                    }
                                }
                            }
                        }
                    }
                }
                stage ("Build merge bot image") {
                    when {
                        anyOf {
                            expression {build_merge_bot_image == 0}
                            expression {FORCE_DOCKER_IMAGE_BUILD.toBoolean() == true}
                        }
                    }
                    steps {
                        script {
                            withEnv(getToolsConfig()) {
                                sh "docker build --build-arg DEFAULT_IMAGE_TAG=${DEFAULT_IMAGE_TAG} --no-cache -t merge_bot_image -f tools/merge_bot/Dockerfile ."
                                if (BRANCH_TO_USE == "master" || BRANCH_TO_USE == "develop") {
                                    sh "docker tag merge_bot_image ${DOCKERHUB_REPO}:merge_bot"
                                    withCredentials([usernamePassword(credentialsId: "dockerhub_id", usernameVariable: "USERNAME", passwordVariable: "PASSWORD")]) {
                                        sh "docker login --username $USERNAME --password $PASSWORD"
                                        sh "docker push ${DOCKERHUB_REPO}:test_image"
                                    }
                                }
                            }
                        }
                    }
                }
                stage ("Pull test image") {
                    when {
                        allOf {
                            expression {build_test_image == 1}
                            expression {FORCE_DOCKER_IMAGE_BUILD.toBoolean() == false}
                        }
                    }
                    steps {
                        script {
                            withEnv(getToolsConfig()) {
                                sh "docker pull ${DOCKERHUB_REPO}:test_image"
                                sh "docker tag ${DOCKERHUB_REPO}:test_image test_image"
                            }
                        }
                    }
                }
                stage ("Build docker compose") {
                    steps {
                        script {
                            sh "docker compose build --no-cache"
                        }
                    }
                }
            }
        }
        stage ("Code analysis") {
            when {
                expression {
                    return REGULAR_BUILD == "true"
                }
            }
            parallel {
                stage ("pylint") {
                    steps {
                        script {
                            sh "docker run --rm test_image python -m pylint src --max-line-length=120 --disable=C0114 --fail-under=9.5"
                            sh "docker run --rm test_image python -m pylint --load-plugins pylint_pytest automated_tests --max-line-length=120 --disable=C0114,C0116 --fail-under=9.5"
                            sh "docker run --rm test_image python -m pylint tools/python --max-line-length=120 --disable=C0114 --fail-under=9.5"
                        }
                    }
                }
                stage ("flake8") {
                    steps {
                        script {
                            sh "docker run --rm test_image python -m flake8 --max-line-length 120 --max-complexity 10 src automated_tests tools/python"
                        }
                    }
                }
                stage ("ruff") {
                    steps {
                        script {
                            sh "docker run --rm test_image python -m ruff check src automated_tests tools/python"
                        }
                    }
                }
                stage ("black") {
                    steps {
                        script {
                            sh "docker run --rm test_image python -m black src automated_tests tools/python"
                        }
                    }
                }
                stage ("bandit") {
                    steps {
                        script {
                            sh "docker run --rm test_image python -m bandit -c automated_tests/bandit.yaml -r src automated_tests tools/python"
                        }
                    }
                }
                stage ("pydocstyle") {
                    steps {
                        script {
                            sh "docker run --rm test_image python -m pydocstyle --ignore D100,D104,D107,D203,D212 ."
                        }
                    }
                }
                stage ("radon") {
                    steps {
                        script {
                            sh "docker run --rm test_image python -m radon cc ."
                            sh "docker run --rm test_image python -m radon mi ."
                            sh "docker run --rm test_image python -m radon hal ."
                        }
                    }
                }
                stage ("mypy") {
                    steps {
                        script {
                            sh "docker run --rm test_image python -m mypy src automated_tests tools/python"
                        }
                    }
                }
                stage ("Code coverage") {
                    steps {
                        script {
                            sh "docker run --name code_coverage_container test_image sh -c 'coverage run --source=src -m pytest -k unittest; coverage html; coverage report --fail-under=95'"
                        }
                    }
                    post {
                        always {
                            sh "docker container cp code_coverage_container:/app/htmlcov ./"
                            sh "docker rm code_coverage_container"
                            archiveArtifacts artifacts: "htmlcov/*"
                        }
                    }
                }
                stage ("Scan for skipped tests") {
                    when {
                        expression {
                            return BRANCH_TO_USE.contains("release") || BRANCH_TO_USE == "master"
                        }
                    }
                    steps {
                        script {
                            sh "docker run --rm test_image python tools/python/scan_for_skipped_tests.py"
                        }
                    }
                }
                stage ("Lint Dockerfiles") {
                    steps {
                        script {
                            withEnv(getToolsConfig()) {
                                sh "chmod +x tools/shell_scripts/lint_docker_files.sh"
                                sh "tools/shell_scripts/lint_docker_files.sh"
                            }
                        }
                    }
                }
                stage ("Shellcheck") {
                    steps {
                        script {
                            withEnv(getToolsConfig()) {
                                sh "chmod +x tools/shell_scripts/lint_shell_scripts.sh"
                                sh "tools/shell_scripts/lint_shell_scripts.sh"
                            }
                        }
                    }
                }
            }
        }
        stage ("Run unit tests") {
            steps {
                script {
                    sh "docker run --name unit_test_container test_image python -m pytest -m unittest automated_tests -v --junitxml=results/unittests_results.xml"
                    sh "docker container cp unit_test_container:/app/results ./"
                }
            }
            post {
                always {
                    sh "docker rm unit_test_container"
                    archiveArtifacts artifacts: "**/unittests_results.xml"
                }
            }
        }
        stage ("Run app & health check") {
            steps {
                script {
                    sh "chmod +x tools/shell_scripts/app_health_check.sh"
                    sh "tools/shell_scripts/app_health_check.sh 30 1"
                }
            }
            post {
                always {
                    sh "docker compose down --rmi all -v"
                }
            }
        }
        stage ("Run tests") {
            matrix {
                axes {
                    axis {
                        name "TEST_GROUP"
                        values "google"
                    }
                }
                stages {
                    stage ("Test stage") {
                        steps {
                            script {
                                if (TEST_GROUPS == "all" || TEST_GROUPS.contains(TEST_GROUP)) {
                                    echo "Running ${TEST_GROUP}"
                                    sh "docker run --name ${TEST_GROUP}_test test_image python -m pytest -m ${FLAG} -k ${TEST_GROUP} automated_tests -v --junitxml=results/${TEST_GROUP}_results.xml"
                                    sh "docker container cp ${TEST_GROUP}_test:/app/results ./"
                                }
                                else {
                                    echo "Skipping execution."
                                }
                            }
                        }
                        post {
                            always {
                                sh "docker rm ${TEST_GROUP}_test"
                                archiveArtifacts artifacts: "**/${TEST_GROUP}_results.xml"
                            }
                        }
                    }
                }
            }
        }
        stage ("Staging") {
            when {
                expression {
                    return REGULAR_BUILD == "true"
                }
            }
            parallel {
                stage ("Push docker image") {
                    when {
                        allOf {
                            expression {BRANCH_TO_USE == "master" || BRANCH_TO_USE == "develop"}
                            expression {IS_NIGHTLY.toBoolean() == false}
                        }
                    }
                    steps {
                        script {
                            docker.withRegistry("", "dockerhub_id") {
                                withEnv(getToolsConfig()) {
                                    sh "docker build --build-arg PYTHON_BASE_IMAGE=python:${DEFAULT_IMAGE_TAG} --no-cache -t custom_image ."
                                    sh "docker tag custom_image ${DOCKERHUB_REPO}:${BRANCH_TO_USE}-${curDate}"
                                    withCredentials([usernamePassword(credentialsId: "dockerhub_id", usernameVariable: "USERNAME", passwordVariable: "PASSWORD")]) {
                                        sh "docker login --username $USERNAME --password $PASSWORD"
                                        sh "docker push ${DOCKERHUB_REPO}:${BRANCH_TO_USE}-${curDate}"
                                        if (BRANCH_TO_USE == "master") {
                                            sh "docker tag custom_image ${DOCKERHUB_REPO}:latest"
                                            sh "docker push ${DOCKERHUB_REPO}:latest"
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
                stage ("Push tag") {
                    when {
                        allOf {
                            expression {BRANCH_TO_USE == "master"}
                            expression {IS_NIGHTLY.toBoolean() == false}
                        }
                    }
                    steps {
                        script {
                            def TAG_NAME = "${BRANCH_TO_USE}-${curDate}"
                            withCredentials([sshUserPrivateKey(credentialsId: "agent_${NODE_NAME}", keyFileVariable: "key")]) {
                                sh 'GIT_SSH_COMMAND="ssh -i $key"'
                                sh "git tag -a $TAG_NAME -m $TAG_NAME && git push origin $TAG_NAME"
                            }
                        }
                    }
                }
            }
        }
    }
    post {
        always {
            sh "docker compose down --rmi all -v"
            sh "docker logout"
            junit allowEmptyResults: true, testResults: "**/**_results.xml"
            publishHTML target: [
                allowMissing: false,
                alwaysLinkToLastBuild: false,
                keepAll: true,
                reportDir: "htmlcov",
                reportFiles: "index.html",
                reportName: "PyTestCov"
            ]
            cleanWs()
        }
    }
}


def getValue(variable, defaultValue) {
    return params.containsKey(variable) ? params.get(variable) : defaultValue
}


def getToolsConfig() {
    return readFile(".tools_config").split("\n") as List
}