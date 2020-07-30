# Watch Exchange Notification System

This is a Python 3.8 based lambda function for querying /r/WatchExchange via the Reddit API. If a keyword is found in the submission title and it has not been seen before a text message notification will be sent.

## Installation
Full lambda deployment package is shown as well as the zip file "watch_exchange_deployment.zip". The zip file can directly be imported into the lambda function and run. 

For the code to work you will need to setup a DynamoDB table, a SNS topic, and an AWS Secret Key (optional but recommended).

## Architecture
<img src="https://github.com/stevenwtolbert/WatchExchangeNotificationSystem/blob/master/images/watchexchange_notification_system_architecture.png" height=100% width=100%>


## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[MIT](https://choosealicense.com/licenses/mit/)