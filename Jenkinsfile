def curDate = new Date().format("yyMMdd-HHmm", TimeZone.getTimeZone("UTC"))
Integer build_test_image
Integer build_merge_bot_image

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
                    def BRANCH_REV = BRANCH_TO_USE.equals("develop") || BRANCH_TO_USE.equals("master") ? "HEAD^1" : "origin/develop"
                    withEnv(getConfig(".tools_config")) {
                        withCredentials([sshUserPrivateKey(credentialsId: "agent_${NODE_NAME}", keyFileVariable: "key")]) {
                            sh 'GIT_SSH_COMMAND="ssh -i $key"'
                            checkout scmGit(branches: [[name: "*/${BRANCH_TO_USE}"]], extensions: [], userRemoteConfigs: [[url: "${REPO_URL}"]])
                        }
                    }
                    withCredentials([file(credentialsId: "cv_credentials", variable: "cv_credentials_file")]) {
                        sh "cp $cv_credentials_file .credentials"
                    }
                    currentBuild.description = "Branch: ${BRANCH_TO_USE}\nFlag: ${FLAG}\nGroups: ${TEST_GROUPS}"
                    build_test_image = sh(script: "git diff --name-only \$(git rev-parse HEAD) \$(git rev-parse ${BRANCH_REV}) | grep -e automated_tests -e src -e requirements -e tools/python",
                                          returnStatus: true)
                    build_merge_bot_image = sh(script: "git diff --name-only \$(git rev-parse HEAD) \$(git rev-parse ${BRANCH_REV}) | grep -e required_reviewers -e src -e requirements/merge_bot -e tools/python/merge_bot.py -e tools/merge_bot/Dockerfile",
                                          returnStatus: true)

                    withEnv(getConfig(".credentials")) {
                        sh "chmod +x tools/shell_scripts/pr_check_status.sh"
                        sh "tools/shell_scripts/pr_check_status.sh ${BRANCH_TO_USE} pending"
                    }
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
                            withEnv(getConfig(".tools_config")) {
                                sh "docker build --build-arg DEFAULT_IMAGE_TAG=${DEFAULT_IMAGE_TAG} --no-cache -t test_image -f automated_tests/Dockerfile ."
                                if (BRANCH_TO_USE == "master" || BRANCH_TO_USE == "develop") {
                                    sh "docker tag test_image ${DOCKERHUB_REPO}:test_image"
                                    withCredentials([usernamePassword(credentialsId: "dockerhub_id", usernameVariable: "USERNAME", passwordVariable: "PASSWORD")]) {
                                        sh "docker login --username $USERNAME --password $PASSWORD"
                                        sh "docker push ${DOCKERHUB_REPO}:test_image"
                                    }
                                }
//                                 else {
//                                     withEnv(getConfig(".credentials")) {
//                                         sh "docker tag test_image ${REGISTRY_URL}/${DOCKERHUB_REPO}:test_image"
//                                         sh "docker push ${REGISTRY_URL}/${DOCKERHUB_REPO}:test_image"
//                                     }
//                                 }
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
                            withEnv(getConfig(".tools_config")) {
                                sh "docker build --build-arg DEFAULT_IMAGE_TAG=${DEFAULT_IMAGE_TAG} --no-cache -t merge_bot_image -f tools/merge_bot/Dockerfile ."
                                if (BRANCH_TO_USE == "master" || BRANCH_TO_USE == "develop") {
                                    sh "docker tag merge_bot_image ${DOCKERHUB_REPO}:merge_bot"
                                    withCredentials([usernamePassword(credentialsId: "dockerhub_id", usernameVariable: "USERNAME", passwordVariable: "PASSWORD")]) {
                                        sh "docker login --username $USERNAME --password $PASSWORD"
                                        sh "docker push ${DOCKERHUB_REPO}:merge_bot"
                                    }
                                }
//                                 else {
//                                     withEnv(getConfig(".credentials")) {
//                                         sh "docker tag merge_bot_image ${REGISTRY_URL}/${DOCKERHUB_REPO}:merge_bot"
//                                         sh "docker push ${REGISTRY_URL}/${DOCKERHUB_REPO}:merge_bot"
//                                     }
//                                 }
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
                            withEnv(getConfig(".tools_config")) {
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
                    return REGULAR_BUILD.toBoolean() == true
                }
            }
            parallel {
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
                stage ("mypy") {
                    steps {
                        script {
                            sh "docker run --rm test_image python -m mypy src automated_tests tools/python"
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
                stage ("radon") {
                    steps {
                        script {
                            sh "docker run --rm test_image python -m radon cc ."
                            sh "docker run --rm test_image python -m radon mi ."
                            sh "docker run --rm test_image python -m radon hal ."
                        }
                    }
                }
                stage ("Code coverage") {
                    steps {
                        script {
                            sh "docker run --name code_coverage_container test_image sh -c 'coverage run --source=src -m pytest -k unittest; coverage html; coverage report --fail-under=85'"
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
                stage ("Test environment check") {
                    when {
                        allOf {
                            expression {build_test_image == 1}
                            expression {FORCE_DOCKER_IMAGE_BUILD.toBoolean() == false}
                        }
                    }
                    steps {
                        script {
                            sh(script: "docker run --rm test_image python -m pytest --collect-only >> in_docker_log.txt")
                            sh(script: "cat in_docker_log.txt")
                            Integer in_docker_value = sh(script: "grep -c '<Function' in_docker_log.txt", returnStdout: true).toInteger()

                            sh(script: "docker run --rm --volume \$(pwd):/pytest_check test_image python -m pytest --collect-only /pytest_check >> in_workdir_log.txt")
                            sh(script: "cat in_workdir_log.txt")
                            Integer in_workdir_value = sh(script: "grep -c '<Function' in_workdir_log.txt", returnStdout: true).toInteger()

                            if (in_docker_value != in_workdir_value) {
                                unstable("Stage reported as unstable.")
                            }
                        }
                    }
                }
                stage ("Lint Dockerfiles") {
                    steps {
                        script {
                            withEnv(getConfig(".tools_config")) {
                                sh "chmod +x tools/shell_scripts/lint_docker_files.sh"
                                sh "tools/shell_scripts/lint_docker_files.sh"
                            }
                        }
                    }
                }
                stage ("Shellcheck") {
                    steps {
                        script {
                            withEnv(getConfig(".tools_config")) {
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
                    sh "tools/shell_scripts/app_health_check.sh 10 1"
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
                        values "add", "subtract", "multiply", "divide", "error"
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
                                sh "docker container cp ${TEST_GROUP}_test:/app/results ./"
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
                    return REGULAR_BUILD.toBoolean() == true
                }
            }
            parallel {
                stage ("Update PR status") {
                    when {
                        expression {
                            return BRANCH_TO_USE.contains("feature") || BRANCH_TO_USE.contains("release")
                        }
                    }
                    steps {
                        script {
                            withEnv(getConfig(".credentials")) {
                                sh "chmod +x tools/shell_scripts/pr_check_status.sh"
                                sh "tools/shell_scripts/pr_check_status.sh ${BRANCH_TO_USE} success"
                            }
                        }
                    }
                }
                stage ("Push docker image") {
                    when {
                        allOf {
                            expression {BRANCH_TO_USE == "master" || BRANCH_TO_USE == "develop"}
                            expression {IS_NIGHTLY.toBoolean() == false}
                        }
                    }
                    steps {
                        script {
                            withEnv(getConfig(".tools_config")) {
                                sh "docker build --build-arg DEFAULT_IMAGE_TAG=${DEFAULT_IMAGE_TAG} --no-cache -t custom_image ."
                                sh "docker tag custom_image ${DOCKERHUB_REPO}:${BRANCH_TO_USE}-${curDate}"
//                                 withEnv(getConfig(".credentials")) {
//                                     echo "${BRANCH_TO_USE.replace("/", "_")}"
//                                     sh "docker tag custom_image ${REGISTRY_URL}/${DOCKERHUB_REPO}:${BRANCH_TO_USE}-${curDate}"
//                                     sh "docker push ${REGISTRY_URL}/${DOCKERHUB_REPO}:${BRANCH_TO_USE}-${curDate}"
//                                 }
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
                stage ("Push tags") {
                    when {
                        allOf {
                            expression {BRANCH_TO_USE == "master" || BRANCH_TO_USE == "develop"}
                            expression {IS_NIGHTLY.toBoolean() == false}
                        }
                    }
                    steps {
                        script {
                            def TAG_NAME = "${BRANCH_TO_USE}-${curDate}"
                            def RELEASE_DESC = BRANCH_TO_USE == "master" ? "Stable ${TAG_NAME}" : "Dev ${TAG_NAME}"
                            def PRE_RELEASE_VALUE = "master" ? "false" : "true"
                            withCredentials([sshUserPrivateKey(credentialsId: "agent_${NODE_NAME}", keyFileVariable: "key")]) {
                                sh 'GIT_SSH_COMMAND="ssh -i $key"'
                                sh "git tag -a $TAG_NAME -m $TAG_NAME && git push origin $TAG_NAME"
                                withEnv(getConfig(".credentials")) {
                                    sh "chmod +x tools/shell_scripts/push_github_tags.sh"
                                    sh "tools/shell_scripts/push_github_tags.sh ${TAG_NAME} ${RELEASE_DESC} ${PRE_RELEASE_VALUE}"
                                }
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
        failure {
            withEnv(getConfig(".credentials")) {
                sh "chmod +x tools/shell_scripts/pr_check_status.sh"
                sh "tools/shell_scripts/pr_check_status.sh ${BRANCH_TO_USE} failure"
            }
        }
    }
}


def getValue(variable, defaultValue) {
    return params.containsKey(variable) ? params.get(variable) : defaultValue
}


def getConfig(fileName) {
    return readFile(fileName).split("\n") as List
}