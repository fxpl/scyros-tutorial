# Copyright 2026 Andrea Gilot
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import streamlit as st
import helpers
from pathlib import Path
import json

RESULTS = Path("results")
KEYWORDS = Path("keywords")
RESULTS.mkdir(exist_ok=True)
KEYWORDS.mkdir(exist_ok=True)


st.set_page_config(page_title="Getting Started with Scyros", page_icon=":wave:")
st.title("Getting Started with Scyros")

st.markdown(
R"""

In this tutorial, we show how to use Scyros to scrape GitHub repositories and extract Java and C functions that use 32-bit and 64-bit integers.

Scyros is a command-line tool designed for large-scale mining of GitHub repositories. It provides several subcommands that allow you to:
- sample repositories from GitHub
- collect repository metadata
- filter repositories based on various criteria
- download relevant source files
- extract and analyze functions from the downloaded code

This tutorial walks through a simplified end-to-end pipeline using these subcommands.

## GitHub Personal Access Token

The first step is to create a GitHub personal access token, which Scyros uses to access the GitHub API.
You can follow the instructions provided by GitHub [here](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens#creating-a-fine-grained-personal-access-token). 
When creating the token, do not grant any additional permissions.
Scyros only requires access to public repository information.
Although the repositories we access are public, GitHub imposes stricter rate limits on anonymous requests. Using a token allows Scyros to make more requests and complete the pipeline faster.

## Running the Tutorial

This tutorial is designed to be interactive and run inside this web application.
Each step will execute the corresponding Scyros command and display the results.

All commands shown in the tutorial can also be run directly from a terminal, where you can view execution logs and progress indicators for steps that may take a long time to complete.

If you are using Docker, you can open a terminal inside the container as described in the README.

## Provide Your Token

Once you have created a GitHub token, paste it into the input box below ___and press Enter___.
""")

ghtoken = st.text_input("GitHub Token", placeholder="Enter your GitHub personal access token here (and press Enter)", type="password")

if ghtoken and st.session_state.get("saved_token") != ghtoken:
    with open("ghtokens.csv", "w", encoding="utf-8") as f:
        f.write("token\n")
        f.write(f"{ghtoken}\n")
    st.session_state["saved_token"] = ghtoken
    st.success("Saved GitHub token to ghtokens.csv")

if ghtoken:
    id = 600

    helpers.run_step("""
    Scyros is a command-line tool written in Rust. The docker container provided with this artifact already contains the compiled binary of Scyros, so you can directly run the commands without installing Rust or compiling the code. 
    To check that Scyros is correctly installed and to see the available subcommands, you can run the following command:""",
    "scyros --help", id, True)
    id += 1

    helpers.run_step("""The first step of the pipeline is to sample random GitHub repositories. You can do this using the `ids` subcommand of Scyros. Every subcommand in Scyros has its own help page, explaining its usage and available options. """,
    "scyros ids --help", id, True)
    id += 1
    
    random_ids = RESULTS / "random_ids.csv"

    helpers.run_step("""Let's scrape 200 random repository IDs using the command below. The list of scraped repositories will be saved in the file `results/random_ids.csv`. 
    The `--force` flag will be used in every command and tells Scyros to overwrite the output file if it already exists. If `--force` is not used, Scyros will resume the previous execution.""",
    f"scyros ids --output {random_ids} --tokens ghtokens.csv -n 200 --force", id)

    id += 1
    if helpers.show_csv(random_ids, "Scraped repository IDs"):
        
        unique_ids = RESULTS / "unique_ids.csv"
        
        helpers.run_step(f"""Since we are sampling random IDs __with__ replacement, some IDs may appear twice (although very unlikely on 200 IDs). 
        Scyros provides a subcommand to remove duplicate IDs. 
        The output will be saved in `{unique_ids}`. """,
        f"scyros duplicate_ids --input {random_ids} --output {unique_ids} --force", id)
        id += 1
        if helpers.show_csv(unique_ids, title="Unique repository IDs"):
            
            non_forked_ids = RESULTS / "non_forked_ids.csv"

            helpers.run_step(f"""Some of the scraped repositories may be forks of other repositories. 
            To avoid analyzing the same code multiple times, we can use Scyros to remove forked repositories from the list. 
            The output will be saved in `{non_forked_ids}`.""",
            f"scyros forks --input {unique_ids} --output {non_forked_ids} --force", id)
            id += 1

            if helpers.show_csv(non_forked_ids, "Non-forked repository IDs"):
                
                metadata = RESULTS / "metadata.csv"

                helpers.run_step(f"""Now we have a list of unique, non-forked repository IDs. 
                The next step is to scrape metadata about these repositories such as their name, creation date, last push date, size, and so on. 
                This can be done using the `metadata` subcommand of Scyros. The output will be saved in `{metadata}`.
                Running this command will take a few minutes, as Scyros needs to make a request to the GitHub API for each repository.
                """,
                f"scyros metadata --input {non_forked_ids} --output {metadata} --tokens ghtokens.csv --force", id)
                id += 1

                if helpers.show_csv(metadata, "Metadata of the scraped repositories"):
                    
                    filter_metadata = RESULTS / "filtered_metadata.csv"

                    st.markdown(f"""We can filter the metadata to keep only repositories with a minimum size and age. 
                    We also filter out repositories that do not contain any code (e.g., repositories that only contain documentation or data).
                    Feel free to change the value of the parameters with the sliders below to see how they affect the results.
                    Note that using values that are too high may result in an empty dataset.
                    The output will be saved in `{filter_metadata}`.""")

                    st.select_slider("Minimum repository size (in kB)", key="size", options=[0, 10, 20, 30, 40, 50, 75, 100, 150, 200, 250, 500, 750, 1000, 10000, 100000, 1_000_000], value=50, help="Minimum size of the repositories to keep, in kilobytes. Repositories with a size smaller than this value will be filtered out.")

                    st.select_slider("Minimum repository age (in days)", key="age", options=[0, 1, 2, 3, 7, 14, 21, 30, 60, 90, 180, 365, 730, 1095, 1825, 3650], value=60, help="Minimum age of the repositories to keep, in days. Repositories that were created less than this number of days ago will be filtered out.")

  

                    helpers.run_command(f"scyros filter_metadata --input {metadata} --output {filter_metadata} --size {st.session_state.size} --age {st.session_state.age} --non-code --force", id)
                    id += 1

                    if helpers.show_csv(filter_metadata, "Filtered metadata of the scraped repositories"):
                        
                        languages = RESULTS / "languages.csv"

                        helpers.run_step(f"""For each repository, we can now scrape the list of languages used in the repository. 
                        Similar to the `metadata` subcommand, this step requires one request to the GitHub API per repository, and thus may take a few minutes. 
                        The output will be saved in `{languages}`.""",
                        f"scyros languages --input {filter_metadata} --output {languages} --tokens ghtokens.csv --force", id)
                        id += 1

                        if helpers.show_csv(languages, "Languages used in the scraped repositories"):
                            
                            keyword_path = KEYWORDS / "int_types.json"

                            st.markdown(f"""Scyros uses JSON files to specify the list of programming languages to keep and the list of keywords to search for in the code.
                            In this small-scale reproduction, we will extract functions using 32 and 64-bit integers in C and Java.
                            A typical keyword file looks like the one below. It contains a list of languages, 
                            each with a list of file extensions and a list of specific keywords to search for in the code. 
                            It also contains a global list of keywords that are not specific to any language.
                            Keyword files must follow this format, otherwise Scyros will not be able to parse them.
                            Let's save this keyword file in `{keyword_path}`. If you are following the tutorial from a terminal, feel free to change the keywords and languages in the JSON file. Avoid using keywords that are too rare or languages that are not very popular, otherwise you may end up with an empty dataset.""")

                            keyword_data = {
                                "languages": [
                                    {
                                        "name": "c",
                                        "extensions": ["c"],
                                        "keywords": []
                                    },
                                    {
                                        "name": "java",
                                        "extensions": ["java"],
                                        "keywords": []
                                    }
                                ],
                                "keywords": ["int", "long"]
                            }

                            json_file = json.dumps(keyword_data, indent=4)

                            st.code(json_file, language="json")

                            # Button to write the file
                            if st.button("Create this file", key="write_keywords"):
                                KEYWORDS.mkdir(exist_ok=True)
                                keyword_path.write_text(json_file, encoding="utf-8")
                                st.success(f"File written to {keyword_path}")
                                
                            if keyword_path.is_file():
                                filtered_languages = RESULTS / "filtered_languages.csv"

                                helpers.run_step(f"""Now we can filter the list of languages to keep only repositories that contain C or Java code.
                                The output will be saved in `{filtered_languages}`.""",
                                f"scyros filter_languages --input {languages} --output {filtered_languages} --languages {keyword_path} --force", id)
                                id += 1

                                if helpers.show_csv(filtered_languages, "Filtered languages of the scraped repositories"):
                                    
                                    fp_projects = RESULTS / "fp_projects.csv"
                                    fp_files = RESULTS / "fp_files.csv"

                                    helpers.run_step(f"""We can now download repositories that contain C or Java code and keep only files written in these languages, and that contain one of the keywords specified in the JSON file (i.e., `int` and `long`).
                                    This command produces two output files: `{fp_projects}`, which contains statistics about the downloaded repositories, and `{fp_files}`, which contains statistics about the downloaded files.
                                    All the files are saved in the destination folder provided as an argument (in this case `target/projects/`), which is created if it does not already exist.
                                    Running this command may take a few minutes, depending on the number of repositories to download and the speed of your internet connection.""",
                                    f"scyros download --input {filtered_languages} --projects {fp_projects} --files {fp_files} --tokens ghtokens.csv --dest target/projects --keywords {keyword_path} --force", id)
                                    id += 1

                                    if helpers.show_csv(fp_projects, "Downloaded projects statistics") and helpers.show_csv(fp_files, "Downloaded files statistics"):
                                        
                                        fp_dedup_files = RESULTS / "fp_dedup_files.csv"
                                        fp_duplicate_map = RESULTS / "fp_duplicate_map.csv"


                                        helpers.run_step(f"""Some files may be duplicated across repositories.
                                        To avoid analyzing the same code multiple times, we can use Scyros to remove duplicate files from the list. 
                                        The output will be saved in `{fp_dedup_files}`, while the mapping between duplicated files and their unique representative will be saved in `{fp_duplicate_map}`. 
                                        The `-s` flag specifies the strategy to use to identify duplicate files.
                                        The `exact` strategy considers two files as duplicates if they are exactly the same, while the `bow` (bag of words) strategy considers two files as duplicates if they contain the same set of words, regardless of their order and frequency. 
                                        """,
                                        f"scyros duplicate_files --input {fp_files} --output {fp_dedup_files} --map {fp_duplicate_map} -s bow --force", id)
                                        id += 1

                                        if helpers.show_csv(fp_dedup_files, "Deduplicated files statistics"):
                                            
                                            fp_functions = RESULTS / "fp_functions.csv"
                                            fp_functions_logs = RESULTS / "fp_functions_logs.csv"

                                            helpers.run_step(f"""Finally, we can parse the unique files to extract the functions they contain and analyze their characteristics.
                                            The output will be saved in `{fp_functions}`, while the number of functions extracted per file is saved in `{fp_functions_logs}`.""",
                                            f"scyros parse --input {fp_dedup_files} --output {fp_functions} --logs {fp_functions_logs} --keywords {keyword_path} --force", id)
                                            id += 1

                                            if helpers.show_csv(fp_functions, "Extracted functions") and helpers.show_csv(fp_functions_logs, "Logs of the function extraction process"):

                                                st.markdown(f"""This concludes the small-scale reproduction study. 
                                                            Now you can use your favorite data analysis tools to analyze the extracted functions and see if you find interesting insights!""")

