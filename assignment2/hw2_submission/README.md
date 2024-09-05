# COMS6998 Spring 2022 HW2 Submission

## Team Members

- J Lin
- S Xie

## Files

### IMPORTANT 1: If you wish to run `./deploy.sh`, do NOT remove or rename any existing files or directories!

### IMPORTANT 2: If you modified the CloudFormation templates and are not sure the templates will work, be sure to run `./delete.sh` and push the code before you run `./deploy.sh`!

- `lambda/lf1.py`: source code of LF1 index photos
- `lambda/lf2.py`: source code of LF2 search photos
- `cf_lambda_pipeline.yml`: CloudFormation template for Lambda Functions' CodePipeline
- `cf_infra.yml`: CloudFormation template for other infra resources (creation triggered by `cf_lambda_pipeline.yml`)
- Deploy the stack(s): `./deploy.sh` (please ignore the deletion errors if it is the first time you deploy it)
- Delete the stack(s): `./delete.sh` (if this failed, you should go to AWS console and delete relevant resources manually)
- `frontend/*`: source code of frontend (please read README.md in there for more information)