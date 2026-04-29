pipeline {
    agent none

    environment {
        IMAGE = 'linux02.local/myapp/flask-demo-1'
        TAG = "build-${BUILD_NUMBER}"

        CHART_REPO = 'linux03.local:3000/admin/flask-demo-1-chart.git'
        CHART_DIR = 'flask-demo-1-chart'
    }

    stages {
        stage('Python CI Check') {
            agent {
                label 'python'
            }

            stages {
                stage('Check Python') {
                    steps {
                        sh 'python3 --version'
                        sh 'pip3 --version'
                    }
                }

                stage('Create Virtualenv') {
                    steps {
                        sh 'python3 -m venv .venv'
                    }
                }

                stage('Install Dependencies') {
                    steps {
                        sh '''
                            . .venv/bin/activate
                            pip install --upgrade pip
                            pip install -r requirements.txt
                        '''
                    }
                }

                stage('Syntax Check') {
                    steps {
                        sh '''
                            . .venv/bin/activate
                            python -m py_compile app.py
                        '''
                    }
                }

                stage('Import Flask App') {
                    steps {
                        sh '''
                            . .venv/bin/activate
                            python -c "import app; print('Flask app import success')"
                        '''
                    }
                }

                stage('Run Flask App and Health Check') {
                    steps {
                        sh '''
                            . .venv/bin/activate

                            nohup python app.py > flask.log 2>&1 &
                            echo $! > flask.pid

                            sleep 5

                            echo "=== flask.log ==="
                            cat flask.log || true

                            echo "=== curl check ==="
                            curl -s http://127.0.0.1:8080/ | tee curl.out

                            grep -q "Hello from Flask Demo" curl.out
                        '''
                    }
                }
            }

            post {
                always {
                    sh '''
                        if [ -f flask.pid ]; then
                            kill $(cat flask.pid) || true
                        fi
                    '''
                }
            }
        }

        stage('Build and Push Image') {
            agent {
                label 'kaniko'
            }

            steps {
                container('kaniko') {
                    sh '''
                        /kaniko/executor \
                          --context "${WORKSPACE}" \
                          --dockerfile "${WORKSPACE}/Dockerfile" \
                          --destination "${IMAGE}:${TAG}" \
                          --registry-certificate=linux02.local=/kaniko/certs/ca.crt
                    '''
                }
            }
        }

        stage('Update Helm Chart Repo') {
            agent {
                label 'python'
            }

            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'gitea-credential',
                    usernameVariable: 'GIT_USER',
                    passwordVariable: 'GIT_PASS'
                )]) {
                    sh '''
                        set -e

                        rm -rf ${CHART_DIR}

                        git clone http://${GIT_USER}:${GIT_PASS}@${CHART_REPO} ${CHART_DIR}

                        cd ${CHART_DIR}

                        git config user.name "jenkins"
                        git config user.email "jenkins@local"

                        sed -i "s|^  repository:.*|  repository: ${IMAGE}|" values.yaml
                        sed -i "s|^  tag:.*|  tag: \\"${TAG}\\"|" values.yaml

                        echo "=== updated values.yaml ==="
                        cat values.yaml

                        git add values.yaml
                        git commit -m "Update image tag to ${TAG}" || echo "No changes to commit"
                        git push origin main
                    '''
                }
            }
        }
    }

    post {
        success {
            echo "镜像已成功推送到 Harbor: ${IMAGE}:${TAG}"
            echo "Helm Chart values.yaml 已更新为 tag: ${TAG}"
            echo "ArgoCD 可以同步部署了"
        }
        failure {
            echo '流水线失败，请查看日志排查'
        }
    }
}