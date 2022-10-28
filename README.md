# steam_analysis

Python/Pandas project on Steam Apps data collection, clean-up and analysis.

The project is WiP.

##  Project goals

There are three main tasks I wanted to accomplish:

 * Streamlining collection of the game information from Steam (and related data sources);
 * Creating an easy-to-use dataset from the collected data;
 * Analyzing the trends on the games and DLCs releases, connections with the price points, user/critic reviews and different features.



# Project structure

| Path                                  | Description                                                                   |
| ------------------------------------- | ----------------------------------------------------------------------------- |
| data/_credentials/                    | Folder Steam API and proxies connections. Contents gitignored                 |
| data/download/                        | Folder with data where it's downloaded to. Contents gitignored                |
| data/export/                          | Folder with the cleaned up datasets, prepared for export. Contents gitignored |
| data/processing/                      | Folder with data being processed by cleanup Notebook. Contents gitignored     |
| notebooks/                            | Folder with processing notebooks                                              |
| notebooks/1-data-collection.ipynb     | Data collection notebook                                                      |
| notebooks/2-cleanup-restructure.ipynb | Clean-up, restructurizing and export for Kaggle                               |
| notebooks/3-analysis-sample.ipynb     | Simple data analysis sample                                                   |
| notebooks/4-code-snippets.ipynb       | Code snippets for tests                                                       |
| notebooks/                            | Folder with processing notebooks                                              |
| scripts/                              | Folder with the automation scripts                                            |
| LICENSE                               | License information                                                           |
| README.md                             | This file                                                                     |

# Data structure

Exported dataset consists of 9 different tables:

#### steam.csv 
Contains most of the numeric information about the Steam Apps from the Steam Storefront with added review scores and tags (collected from Reviews API and SteamSpy)

#### steam\_description\_data.csv
App descriptions as they are shown in Steam

#### steam\_media\_data.csv
Links to screenshots, images and trailers

#### steam\_optional.csv
Notices, content descriptors, Metacritic information and demos

#### steam\_packages\_info.csv
Game packages (**NOT bundles**, they are unavailable from Storefront)

#### steam\_requirements\_data.csv
Game requirements

#### steam\_support\_info.csv
e-mail/website support links

#### steamspy\_tags\_data.csv
SteamSpy tags and the number of votes for each tag for each game. 

#### missing\_ids.csv
Contains information on AppIDs I was unable to collect or removed during the data cleanup with possible reason.

# Acknowledgements
Huge props to [Nick Davis](https://nik-davis.github.io) for making the clean Steam Data dataset and thoroughly describing the process in his blog and [Vicente Arce](https://twitter.com/Duerkos) for making awesome notebooks this work is forked from.

# TODO:
-   Streamlining collection scripts
-   Automating clean-ups
-   Analysis notebooks
-   Add NLP analysis? 