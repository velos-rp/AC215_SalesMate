# LLM Fine-tuning

The purpose of this container is to fine tune an LLM model on real call transcripts so that the AI behaves more like the customers of our potential clients. In order do do that we have two major steps:

1. Process data
2. Train model

Each of the steps will be further detailed below. 

The code in this folder spins up a container with all the required code. Specific commands can then be sent to process data and to train the model. This container is indepenpent from the other containers and is only used when training the model. In contrast, all the other containers of this application must be spin up while the app is running and are managed by the Dockercompose file in the root of this repo. 


## Process data

We got access to 1235 sales calls, which we used as input to finetune the model. Those calls were made by a Brazilian company and therefore were all in Portuguese. This data is stored in a csv file located in a bucket inside GCP: ac215_salesmate/data/extract_calls_pt.csv. A sample of this data is located in the data folder of this repo. Each row represents a call and the column "transcript" has the transcript of the call. It is structured as a list of dictionaries where each dictionary is a turn of speech from the seller or the buyer. 

The following are the steps to process this data:

1. Translation: We use Google translation API to translate all csv to english
2. Generation of dataset: We put the data in the shape that Vertex AI needs to make the finetuning, where each row is a single round of conversation from both seller and cliet, instead of multiple rounds
3. Train test split and sampling: we split the dataset in 1k examples of train and 1k examples of test
4. Formatting and saving: We format the datasets as jsol and save to the GCP bucket as sample-calls_sample_1k_test.jsonl and sample-calls_sample_1k_train.jsonl. They are also located in the data folder of this repo. 

## Train model
We use Vertex AI to train the model. It reads the jsonl files from the bucket and then train and host the model in VertexAI. We need then to see the ID of the model to set it up in the configurations from the api_service container since it uses the hosted model to generate the responses. 


## Directions to run finetune-pipeline:

1. Run `bash docker-shell.sh`. This will spin up the container. 
2. Inside the container run python cli.py --process_data --data_path ac215_salesmate/data/extract_calls_pt.csv to process the data. 
3. Inside the container run python cli.py --train to train the model
4. (Optional) Note down the endpoint from the trained model and update it in the chat() function inside cli.py. nside the container run python cli.py --chat to test the model. 