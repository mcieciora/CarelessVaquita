def testImage

pipeline {
    agent any
    environment {
        FLAG = getValue("FLAG", "smoke")
        TEST_GROUPS = getValue("TEST_GROUP", "all")
        REGULAR_BUILD = getValue("REGULAR_BUILD", true)
        BRANCH_TO_USE = getValue("BRANCH", env.BRANCH_NAME)
        REPO_URL = "git@github.com:mcieciora/CarelessVaquita.git"
    }
    options {
        skipDefaultCheckout()
    }
    stages {
        stage ("Checkout branch") {
            steps {
                script {
                    withCredentials([sshUserPrivateKey(credentialsId: "github_id", keyFileVariable: 'key')]) {
                        sh 'GIT_SSH_COMMAND="ssh -i $key"'
                        git branch: env.BRANCH_TO_USE, url: env.REPO_URL
                    }
                    currentBuild.description = "Branch: ${env.BRANCH_TO_USE}\nFlag: ${env.FLAG}\nGroups: ${env.TEST_GROUPS}"
                }
            }
        }
        stage ("Prepare docker images") {
            parallel {
                stage("Build test image") {
                    steps {
                        script {
                            testImage = docker.build("test_image:${env.BUILD_ID}", "-f automated_tests/Dockerfile .")
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
        stage("Code analysis") {
            when {
                expression {
                    return env.REGULAR_BUILD == "true"
                }
            }
            parallel {
                stage ("Pylint") {
                    steps {
                        script {
                            testImage.inside("-v $WORKSPACE:/app") {
                                sh "python3 -m pylint src --max-line-length=120 --disable=C0114 --fail-under=9.5"
                                sh "python3 -m pylint --load-plugins pylint_pytest automated_tests --max-line-length=120 --disable=C0114,C0116 --fail-under=9.5"
                                sh "python3 -m pylint tools/python --max-line-length=120 --disable=C0114 --fail-under=9.5"
                            }
                        }
                    }
                }
                stage ("flake8") {
                    steps {
                        script {
                            testImage.inside("-v $WORKSPACE:/app") {
                                sh "python3 -m flake8 --max-line-length 120 --max-complexity 10 src"
                            }
                        }
                    }
                }
                stage ("ruff") {
                    steps {
                        script {
                            testImage.inside("-v $WORKSPACE:/app") {
                                sh "python3 -m ruff format ."
                                sh "python3 -m ruff check ."
                            }
                        }
                    }
                }
                stage ("black") {
                    steps {
                        script {
                            testImage.inside("-v $WORKSPACE:/app") {
                                sh "python3 -m black ."
                            }
                        }
                    }
                }
                stage("Code coverage") {
                    steps {
                        script {
                            testImage.inside("-v $WORKSPACE:/app") {
                                sh "python3 -m pytest --cov=src automated_tests/ --cov-fail-under=95 --cov-report=html"
                            }
                            publishHTML target: [
                                allowMissing: false,
                                alwaysLinkToLastBuild: false,
                                keepAll: true,
                                reportDir: "htmlcov",
                                reportFiles: "index.html",
                                reportName: "PyTestCov"
                            ]
                        }
                    }
                }
                stage ("Scan for skipped tests") {
                    when {
                        expression {
                            return env.BRANCH_NAME == "release" || env.BRANCH_NAME == "master"
                        }
                    }
                    steps {
                        script {
                            testImage.inside("-v $WORKSPACE:/app") {
                                sh "python3 tools/python/scan_for_skipped_tests.py"
                            }
                        }
                    }
                }
            }
        }
        stage ("Run unit tests") {
            steps {
                script {
                    testImage.inside("-v $WORKSPACE:/app") {
                        sh "python3 -m pytest -m unittest automated_tests -v --junitxml=results/unittests_results.xml"
                    }
                }
            }
        }
        stage("Run tests") {
            matrix {
                axes {
                    axis {
                        name "TEST_GROUP"
                        values "google"
                    }
                }
                stages {
                    stage("Test stage") {
                        steps {
                            script {
                                if (env.TEST_GROUPS == "all" || env.TEST_GROUPS.contains(TEST_GROUP)) {
                                    echo "Running ${TEST_GROUP}"
                                    testImage.inside("-v $WORKSPACE:/app") {
                                        sh "python3 -m pytest -m ${FLAG} -k ${TEST_GROUP} automated_tests -v --junitxml=results/${TEST_GROUP}_results.xml"
                                    }
                                }
                                else {
                                    echo "Skipping execution."
                                }
                            }
                        }
                    }
                }
            }
        }
        stage ("Staging") {
            when {
                expression {
                    return env.REGULAR_BUILD == "true"
                }
            }
            stages {
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
                stage ("Push docker image") {
                    when {
                        expression {
                            return env.BRANCH_NAME == "master" || env.BRANCH_NAME == "develop"
                        }
                    }
                    steps {
                        script {
                            def registryPath = ""
                            def containerName = "mcieciora/careless_vaquita:${env.BRANCH_NAME}_${env.BUILD_ID}"
                            if (env.BRANCH_NAME == "develop") {
                                registryPath = "http://localhost:5000"
                                containerName = "careless_vaquita:${env.BRANCH_NAME}_${env.BUILD_ID}"
                            }
                            docker.withRegistry("${registryPath}", "dockerhub_id") {
                                def customImage = docker.build("${containerName}")
                                customImage.push()
                            }
                            sh "docker rmi ${containerName}"
                        }
                    }
                }
                stage ("Push tag") {
                    when {
                        expression {
                            return env.BRANCH_NAME == "master"
                        }
                    }
                    steps {
                        script {
                            def TAG_NAME = "${env.BRANCH_NAME}_${env.BUILD_ID}"
                            withCredentials([sshUserPrivateKey(credentialsId: "github_id", keyFileVariable: 'key')]) {
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
            sh "docker rmi test_image:${env.BUILD_ID}"
            sh "docker compose down --rmi all -v"
            archiveArtifacts artifacts: "**/*_results.xml"
            junit "**/*_results.xml"
            dir("${WORKSPACE}") {
                deleteDir()
            }
        }
    }
}


def getValue(variable, defaultValue) {
    return params.containsKey(variable) ? params.get(variable) : defaultValue
}