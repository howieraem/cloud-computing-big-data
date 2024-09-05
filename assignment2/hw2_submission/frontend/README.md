### Install dependencies

`yarn install`

### Edit environment variables

Change `REACT_APP_API_GATEWAY_ID`, `REACT_APP_API_GATEWAY_STAGE` and `REACT_APP_AWS_REGION` in both `start.sh` and `build.sh` accordingly.

### Run from the root directory

`./start.sh`

### Build static files for deployment

Run `./build.sh` which will produce a `build` folder. Upload all folders and files in the `build` folder to a S3 bucket for static web hosting.
