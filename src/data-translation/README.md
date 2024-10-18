The main purpose of this container is to translate the sample dataset of 1235 sales calls and their transcriptions that are in Portugese to English. The incoming data are in a specific csv format and the CLI interface `cli.py` loads the csv as a Pandas dataframe and runs the Google Cloud Translation API on each row. The results are stored in new dataframe columns and the aggregate dataframe is saved to a csv file. 

Directions to run the data-translation container:
1. Start a new terminal from the root project directory.
2. `cd src/data-translation`
2. Execute `sh docker-shell.sh`
3. Ensure that the CSV to be processed is located in a local `data` directory.
4. Execute `python cli.py data/data.csv` - This will process the data in `data/data.csv` and save the results in `output/data_translated.csv`.