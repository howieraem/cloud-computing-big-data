const API_GATEWAY = `https://${process.env.REACT_APP_API_GATEWAY_ID}.execute-api.${process.env.REACT_APP_AWS_REGION}.amazonaws.com/${process.env.REACT_APP_API_GATEWAY_STAGE}`;
console.log(`[DEBUG] API Gateway Endpoint: ${API_GATEWAY}`);
export const API_SEARCH = API_GATEWAY + "/search";
export const API_UPLOAD = API_GATEWAY + "/photos";
export const API_KEY = "yutyJVZgG92YApBOPmKg08y9KobJiYaI9uMQ6H5S";