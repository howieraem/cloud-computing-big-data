const https = require('https');
const AWS = require('aws-sdk');

async function lexClient(message, usrId) {
    const botAlias = '$LATEST';
    const botName = 'OrderFlowers';
    const sessionAttributes = {};

    const lexruntime = new AWS.LexRuntime({
      region: process.env.REGION
    });

    const params = {
  	  botAlias: process.env.BOT_ALIAS,
  	  botName: process.env.BOT_NAME,
  	  inputText: message,
  	  userId: usrId,
  	  sessionAttributes: {}
  	};

    const data = await lexruntime.postText(params).promise();
    // console.log(JSON.stringify(data));
    return data.message;
}

exports.handler = async (event) => {
  const message = JSON.parse(event.body).messages[0].unstructured;
  const date = new Date();
  const usrId = event.headers['X-Forwarded-For'];
	const replyMessage = await lexClient(message.text, usrId);
	
	const response = {
    statusCode: 200,
    headers: {
      "Access-Control-Allow-Headers" : "Authorization, Content-Type",
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "POST,GET"
    },
    body: JSON.stringify({
      "messages": [{
          "type": "unstructured",
          "unstructured": {
              "id": "0",
              "text": replyMessage,
              "timestamp": date.toISOString()
          }
      }]
    })
  };
  return response;
};