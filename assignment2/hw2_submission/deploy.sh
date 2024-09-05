sh ./delete.sh
aws --region us-east-1 cloudformation deploy --template-file cf_lambda_pipeline.yml --stack-name hw2-demo-lambda-pipeline --capabilities CAPABILITY_NAMED_IAM
aws --region us-east-1 cloudformation wait stack-create-complete --stack-name hw2-demo-lambda-pipeline

rm -f tmp
cnt=0

while [ $cnt -lt 8 ]
do
    echo "Waiting for Lambda Functions' CodePipeline execution to complete..."
    aws codepipeline get-pipeline-state --name hw2-demo-lambda-pipeline >> tmp
    cnt=$(grep "Succeeded" tmp | wc -l)
    rm -f tmp
    sleep 15
done

aws --region us-east-1 cloudformation wait stack-create-complete --stack-name hw2-demo-infra

cnt=0

while [ $cnt -lt 6 ]
do
    echo "Waiting for Frontend's CodePipeline execution to complete..."
    aws codepipeline get-pipeline-state --name hw2-demo-infra-frontend-pipeline >> tmp
    cnt=$(grep "Succeeded" tmp | wc -l)
    rm -f tmp
    sleep 15
done

aws --region us-east-1 cloudformation describe-stacks --stack-name hw2-demo-infra --query "Stacks[0].Outputs[?OutputKey=='APIGatewayEndpoint'].OutputValue" --output text
aws --region us-east-1 cloudformation describe-stacks --stack-name hw2-demo-infra --query "Stacks[0].Outputs[?OutputKey=='WebsiteURL'].OutputValue" --output text