

i'm trying to migrate a few projects to aws in a way that i can also develop and troubleshoot it locally. the infrastucture should be defined using cdk with python. there should be a authentication stack for cognito. i'm planning to use the app-dw.net domain as the root domain. authentication should happen on the auth subdomain and should be used to authenticate to all projects. the lang portal should be available at the lang-portal subdomain, the haiku generator app at haiku subdomain, the vocab generator app at vocab, and the writing practice app at writing. the react frontends should be built and pushed to an s3 bucket and served from a cloudfront distribution. the backends should available at the same subdomain as the frontend but from the /api path and be a load balancer or api gateway and not exposed directly. both frontend and backend should have a build pipeline to build them based on changes in the github repo. this project uses a mono-repo approach with all code contained in https://github.com/danielwohlgemuth/free-genai-bootcamp-2025/, so there need to be a filter for the right folder. for example, the lang poratl backend is in the /aws/lang-portal-backend folder and the lang portal frontend in the /aws/lang-portal-frontend folder.

these are the projects that need to be migrated:
haiku-generator-backend
haiku-generator-frontend
lang-portal-backend
lang-portal-frontend
vocab-generator-backend
vocab-generator-frontend
writing-practice-frontend

haiku-generator-frontend and lang-portal-frontend are react apps
haiku-generator-backend, lang-portal-backend, vocab-generator-backend are python apps that expose an api using fastapi
vocab-generator-frontend is a python app using streamlit
writing-practice-frontend is a python app using gradio

most of the apps use ollama as the llm service. it should be replaced with aws bedrock
sqlite should be replaced with aws rds using the postgres engine
the python apps should be hosted on ecs
for simplicity, there should only be one environment where everything gets deployed to
audio generation should use polly
image generation should use an aws hosted solution
minio should be replaced with s3
llm calls should be enhanced to include guardrails
there should be a stack for each project thatn needs to be migrated and possibly additional ones like the one for cognito
include a mermaid flow diagram with the components for each project. use a representative emoji and the name of the service for each node.

