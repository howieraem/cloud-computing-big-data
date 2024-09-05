aws s3 rb --force s3://hw2-demo-b1-frontend-storage-dev
aws s3 rb --force s3://hw2-demo-b2-photo-storage-dev
aws s3 rb --force s3://hw2-demo-frontend-cicd-storage
aws s3 rb --force s3://hw2-demo-lambda-cicd-storage
sleep 15
aws cloudformation delete-stack --stack-name hw2-demo-infra
aws cloudformation wait stack-delete-complete --stack-name hw2-demo-infra
aws cloudformation delete-stack --stack-name hw2-demo-lambda-pipeline
aws cloudformation wait stack-delete-complete --stack-name hw2-demo-lambda-pipeline