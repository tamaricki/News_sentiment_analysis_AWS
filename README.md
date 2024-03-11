# News Sentiment Analysis On AWS Lambda

Outcome of the project is streamlit dashboard showing sentiment of sport news published in last 24 hours coming from the news API. In order to deploy this app to the public, following things are done: 
* Setting up the news API
* Creating on AWS RDS Postgres DB
* Creating S3 bucket as raw storage
* Create Lambda functions which extracts and analyses the news sends the news and sentiment results to Postgres DB as well as in S3 storage
* Schedule Lambda with EventBridge
* Streamlit app creation and local test
* Docker image creation and dependency management with poetry
* Setting up ECR (Elastic Container Registry)
* Pushing created docker image to ECR and deploying it to Fargate Elastic Container service



### Design

![alt text]()


### Useful Links 

https://alpopkes.com/posts/python/packaging_tools/ 
https://docs.aws.amazon.com/AmazonECS/latest/developerguide/task_execution_IAM_role.html 
https://newsapi.org/ 
https://docs.aws.amazon.com/lambda/latest/dg/chapter-layers.html
https://aws.amazon.com/premiumsupport/knowledge-center/lambda-layer-simulated-docker/ 

