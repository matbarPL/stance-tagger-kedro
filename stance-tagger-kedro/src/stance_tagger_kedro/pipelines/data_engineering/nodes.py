# Copyright 2020 QuantumBlack Visual Analytics Limited
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, AND
# NONINFRINGEMENT. IN NO EVENT WILL THE LICENSOR OR OTHER CONTRIBUTORS
# BE LIABLE FOR ANY CLAIM, DAMAGES, OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF, OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
# The QuantumBlack Visual Analytics Limited ("QuantumBlack") name and logo
# (either separately or in combination, "QuantumBlack Trademarks") are
# trademarks of QuantumBlack. The License does not grant you any right or
# license to the QuantumBlack Trademarks. You may not use the QuantumBlack
# Trademarks or any confusingly similar mark as a trademark for your product,
#     or use the QuantumBlack Trademarks in any other manner that might cause
# confusion in the marketplace, including but not limited to in advertising,
# on websites, or on software.
#
# See the License for the specific language governing permissions and
# limitations under the License.
"""Example code for the nodes in the example pipeline. This code is meant
just for illustrating basic Kedro features.

PLEASE DELETE THIS FILE ONCE YOU START WORKING ON YOUR OWN PROJECT!
"""

from typing import Any, Dict

import pandas as pd
import numpy as np
import csv

def prepare_dataset(data: pd.DataFrame, method_flag: str) -> Dict[str,pd.DataFrame]:
    """Node for preparing dataset in fasttext format which is
    __label__<var1> text"""
    data["Target"] = data["Target"].apply(lambda x: x.replace(" ", "_").lower())
    if method_flag == "favour_against":
        data["label"] = data["Stance"].map({"FAVOR":"__label__favour",
                                          "AGAINST":"__label__against",
                                          "NONE": "__label__none"})
    elif method_flag == "classification":
        data["label"] = "__label__" + data["Target"]
    elif method_flag == "opinion_towards":
        data["label"] = data["Opinion towards"].map({"TARGET": "__label__target",
                                            "OTHER": "__label__other",
                                            "NO ONE": "__label__noone"})
    elif method_flag == "sentiment":
        data["label"] = data["Sentiment"].map({"POSITIVE": "__label__positive",
                                                 "NEGATIVE": "__label__negative",
                                                 "NEITHER": "__label__neither"})
    data["Final"] = data["label"] + " " + data["Tweet"]
    return dict(final_dataset=pd.DataFrame(data["Final"]))


def split_data(data: pd.DataFrame, method_flag: str, example_test_data_ratio: float) -> Dict[str, Any]:
    """Node for splitting the prepared dataset into training and test sets.
    The dataset is the prepared dataset for fasttext format.
    The split ratio parameter is taken from conf/project/parameters.yml.
    The data and the parameters will be loaded and provided to your function
    automatically when the pipeline is executed and it is time to run this node.
    """
    # Split to training and testing data
    dict_split = split_train_test(data, example_test_data_ratio, method_flag)

    train_data = dict_split["train_data"]
    test_data = dict_split["test_data"]

    # When returning many variables, it is a good practice to give them names:
    return dict(
        train=train_data,
        test=test_data
    )

def split_train_test(data:pd.DataFrame, example_test_data_ratio: float, method_flag: str) -> Dict[str, str]:
    """Temporary function for splitting data into train and test dataframe"""
    n = data.shape[0]
    n_test = int(n * example_test_data_ratio)
    training_data = data.iloc[n_test:, :].reset_index(drop=True) #to be changed not to take first rows only for test
    training_data_path = "data/05_model_input/stance."+method_flag+".train.preprocessed.tokenized.txt"
    training_data.dropna(inplace=True)
    training_data[["Final"]].to_csv(
        training_data_path,
        header=None, index=False, sep="|",
        quoting=csv.QUOTE_NONE,
        quotechar='', escapechar='\\')
    test_data = data.iloc[:n_test, :].reset_index(drop=True)
    test_data_path = "data/05_model_input/stance"+method_flag+".test.preprocessed.tokenized.txt"
    test_data.dropna(inplace=True)
    test_data[["Final"]].to_csv(
        test_data_path,
        header=None, index=False, sep="|",
        quoting=csv.QUOTE_NONE,
        quotechar='', escapechar='\\')
    return dict(
        train_data=training_data_path,
        test_data=test_data_path
    )