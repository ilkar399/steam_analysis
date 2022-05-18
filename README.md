# steam_analysis

Python/Pandas project on Steam Apps data collection, clean-up and analysis.

The project is WiP.

# Project structure:

| Path                                    | Description                                                                   |
| --------------------------------------- | ----------------------------------------------------------------------------- |
| data/_credentials/                      | Folder Steam API and proxies connections. Contents gitignored                 |
| data/download/                          | Folder with data where it's downloaded to. Contents gitignored                |
| data/export/                            | Folder with the cleaned up datasets, prepared for export. Contents gitignored |
| data/processing/                        | Folder with data being processed by cleanup Notebook. Contents gitignored     |
| notebooks/                              | Folder with processing notebooks                                              |
| notebooks/1-data-collection.ipynb   | Data collection notebook                                                      |
| notebooks/2-0-cleanup-restructure.ipynb | Clean-up, restructurizing and export for Kaggle                               |
| notebooks/                              | Folder with processing notebooks                                              |
| scripts/                                | Folder with processing scripts                                                |
| LICENSE                                 | License information                                                           |
| README.md                               | This file                                                                     |

# Acknowledgements
Huge props to [Nick Davis](https://nik-davis.github.io) for making the clean Steam Data dataset and thoroughly describing the process in his blog and [Vicente Arce](https://twitter.com/Duerkos) for making awesome notebooks this work is forked from.

# TODO:
-   Adding timestamps on collection
-   Streamlining collection scripts
-   Automating clean-ups
-   Analysis notebook
-   Add NLP analysis? 