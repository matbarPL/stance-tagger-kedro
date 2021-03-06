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

Delete this when you start working on your own Kedro project.
"""

from kedro.pipeline import Pipeline, node

from .nodes import split_data
from .nodes import prepare_dataset

def create_pipeline(**kwargs):
    return Pipeline(
        [
            node(
                prepare_dataset,
                ["stances_data", "params:model_classification_name"],
                dict(
                    final_dataset="preprocessed_data_classification"
                ),
            ),
            node(
                prepare_dataset,
                ["stances_data", "params:model_favour_against_name"],
                dict(
                    final_dataset="preprocessed_data_favour_against"
                ),
            ),
            node(
                prepare_dataset,
                ["stances_data", "params:model_opinion_towards_name"],
                dict(
                    final_dataset="preprocessed_data_opinion_towards"
                ),
            ),
            node(
                prepare_dataset,
                ["stances_data", "params:model_sentiment_name"],
                dict(
                    final_dataset="preprocessed_data_sentiment"
                ),
            ),
            node(
                split_data,
                ["preprocessed_data_classification", "params:model_classification_name",
                 "params:example_test_data_ratio"],
                dict(
                    train="classification_train",
                    test="classification_test",
                ), #to the test variable classification_train name will be assigned
            ),
            node(
                split_data,
                ["preprocessed_data_favour_against", "params:model_favour_against_name",
                 "params:example_test_data_ratio"],
                dict(
                    train="favour_against_train",
                    test="favour_against_test",
                ),  # to the test variable classification_train name will be assigned
            ),
            node(
                split_data,
                ["preprocessed_data_opinion_towards", "params:model_opinion_towards_name",
                 "params:example_test_data_ratio"],
                dict(
                    train="opinion_towards_train",
                    test="opinion_towards_test",
                ), #to the test variable classification_train name will be assigned
            ),
            node(
                split_data,
                ["preprocessed_data_sentiment", "params:model_sentiment_name",
                 "params:example_test_data_ratio"],
                dict(
                    train="sentiment_train",
                    test="sentiment_test",
                ),  # to the test variable classification_train name will be assigned
            )
        ]
    )

