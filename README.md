# Advance-Image-Downloader-or-Extractor-Job
This project contains an Image scraper that can query Google Images and then scrape
and save a specified number of results to an AWS S3 Bucket specified by the user.

## The Source Code
The src code for this project is found in the [app](./Image%20Scraper/app) directory; [app.py](./Image%20Scraper/app/app.py)
contains the lambda function handler and modules [scraper](./Image%20Scraper/app/scraper) and [aws_s3](./Image%20Scraper/app/aws_s3)
are helper modules for image scraping and persisting to S3 respectively.

## The Dockerfile and building the image
The [Dockerfile](./Image%20Scraper/Dockerfile) contains the instructions to build this image. You can
run the command to create the image lambda/image-scraper version 1.0
```
docker build -t lambda/image-scraper:1.0 .
```

## Running and experimenting locally
The image can be run locally before you deploy to deploy to AWS Lambda. Providing
you already have AWS credentials setup in `~/.aws/credentials` you can simply run the
command.
```
docker run -p 9000:8080 -v ~/.aws/:/root/.aws/ lambda/image-scraper:1.0
```
The -v flag mounts your local AWS credentials into the docker container allowing it access
to your AWS account and S3 bucket.

To confirm the container is working as it should locally, you can run a similar command to
```
curl -XPOST "http://localhost:9000/2015-03-31/functions/function/invocations" -d '{"query":"Himalyan Tiger", "count":10
, "bucket":"tiger", "folder_path":"images/"}'
```
This command intends to query google images for 'Himalyan Tiger', scrape the first 10 images
returned and then persist them to a bucket called 'tiger' within a 'folder' called
'images'. A successful result should return something like this...
```
"Successfully loaded 10 images to bucket tiger. Folder path images/ and file names ['6jdejbda7a.jpeg', 'fsagh5j54d.jpeg
', 'dfg1b6065le.jpeg','wr1bfg065er.jpeg', .........]."
```
The image names are based on a hash of their data so the names are likely to differ. You can also 
verify the result by checking your S3 bucket on AWS.

*Note : You first have to create an S3 bucket in your AWS account and give the required permission of access. Also enter your aws credentials wherever mentioned in the script*

## Deploying to Lambda.
AWS Lambda can now take an image to run as a serverless function. For extra help, AWS have published a guide to working with containers in 
Lambda https://docs.aws.amazon.com/lambda/latest/dg/lambda-images.html.

You will also need to create an Elastic Container Registry within AWS - a place to 
store your Docker images so they can be used by Lambda. For extra help, AWS have published
a guide to working with ECR https://docs.aws.amazon.com/AmazonECR/latest/userguide/getting-started-cli.html.

Create a 2nd Lambda Function and copy the code from [lamda2](./lamda2.py) .This contains the code to zip the images and create a presigned url to be mailed to the client(or yourself).

## Create a Step funtion State Machine
Create a step function to invoke the two lambda functions one by one . You can change the input (i.e. search query,count etc.) in the payload section of json input given in Step Function.

## Debugging - Gotchas and Quick Fixes
Once running your container on Lambda you may get an error message. This may be a result of a short
timeout period and low memory capacity. I use a timeout period of 60 seconds and a
500Mb allocation of memory to be on the safe side. I am only scraping 10-20 images per request. You
may need to adjust your timeout and memory needs accordingly.

## Project Deployment Demo Video

https://youtu.be/pGK9_2yub7U


