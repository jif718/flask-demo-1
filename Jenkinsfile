pipeline {
    agent none

    environment {
        ECR_REGISTRY = '445529239852.dkr.ecr.ap-east-1.amazonaws.com'
        IMAGE_NAME   = 'myapp/flask-demo-1'
        IMAGE        = "${ECR_REGISTRY}/${IMAGE_NAME}"
        TAG          = "build-${BUILD_NUMBER}"
    }

    stages {
        stage('Python CI Check') {
            agent {
                label 'python'
            }

            stages {
                stage('Check Python') {
                    steps {
                        container('python') {
                            sh 'python3 --version'
                            sh 'pip3 --version'
                        }
                    }
                }

                stage('Create Virtualenv') {
                    steps {
                        container('python') {
                            sh 'python3 -m venv .venv'
                        }
                    }
                }

                stage('Install Dependencies') {
                    steps {
                        container('python') {
                            sh '''
                                . .venv/bin/activate
                                pip install --upgrade pip
                                pip install -r requirements.txt
                            '''
                        }
                    }
                }

                stage('Syntax Check') {
                    steps {
                        container('python') {
                            sh '''
                                . .venv/bin/activate
                                python -m py_compile app.py
                            '''
                        }
                    }
                }

                stage('Import Flask App') {
                    steps {
                        container('python') {
                            sh '''
                                . .venv/bin/activate
                                python -c "import app; print('Flask app import success')"
                            '''
                        }
                    }
                }

                stage('Run Flask App and Health Check') {
                    steps {
                        container('python') {
                            sh '''
                                . .venv/bin/activate

                                nohup python app.py > flask.log 2>&1 &
                                echo $! > flask.pid

                                sleep 5

                                echo "=== flask.log ==="
                                cat flask.log || true

                                echo "=== health check via python urllib ==="
                                python <<'PYEOF'
import urllib.request
resp = urllib.request.urlopen('http://127.0.0.1:8080/').read().decode()
print(resp)
assert 'Hello from Flask Demo' in resp, 'health check failed'
print('health check OK')
PYEOF
                            '''
                        }
                    }
                }
            }

            post {
                always {
                    container('python') {
                        sh '''
                            if [ -f flask.pid ]; then
                                kill $(cat flask.pid) || true
                            fi
                        '''
                    }
                }
            }
        }

        stage('Build and Push to ECR') {
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
                          --destination "${IMAGE}:latest" \
                          --cache=true \
                          --cache-repo "${ECR_REGISTRY}/${IMAGE_NAME}/cache" \
                          --verbosity info
                    '''
                }
            }
        }
    }

    post {
        success {
            echo "Image pushed to ECR: ${IMAGE}:${TAG}"
            echo "Image pushed to ECR: ${IMAGE}:latest"
        }
        failure {
            echo 'Pipeline failed, check logs above'
        }
    }
}