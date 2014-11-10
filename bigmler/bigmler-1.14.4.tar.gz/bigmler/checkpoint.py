# -*- coding: utf-8 -*-
#
# Copyright 2012-2014 BigML
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""Checkpoint functions for BigMLer

"""
from __future__ import absolute_import

import os

import bigml.api

from bigml.util import console_log

from bigmler.utils import log_message


def is_source_created(path, suffix=""):
    """Checks existence and reads the source id from the source file in the
       path directory

    """
    source_id = None
    try:
        with open("%s%ssource%s" % (path, os.sep, suffix)) as source_file:
            source_id = source_file.readline().strip()
            try:
                source_id = bigml.api.get_source_id(source_id)
                return True, source_id
            except ValueError:
                return False, None
    except IOError:
        return False, None


def is_dataset_created(path, suffix=""):
    """Checks existence and reads the dataset id from the dataset file in
       the path directory

    """
    dataset_id = None
    try:
        with open("%s%sdataset%s" % (path, os.sep, suffix)) as dataset_file:
            dataset_id = dataset_file.readline().strip()
            try:
                dataset_id = bigml.api.get_dataset_id(dataset_id)
                return True, dataset_id
            except ValueError:
                return False, None
    except IOError:
        return False, None


def are_datasets_created(path, number_of_datasets, suffix='parts'):
    """Checks existence and reads the dataset ids from the datasets file in
       the path directory

    """
    dataset_ids = []
    try:
        with open("%s%sdataset_%s" % (path, os.sep, suffix)) as datasets_file:
            for line in datasets_file:
                dataset = line.strip()
                try:
                    dataset_id = bigml.api.get_dataset_id(dataset)
                    dataset_ids.append(dataset_id)
                except ValueError:
                    return False, dataset_ids
        if len(dataset_ids) == number_of_datasets:
            return True, dataset_ids
        else:
            return False, dataset_ids
    except IOError:
        return False, dataset_ids


def are_models_created(path, number_of_models):
    """Checks existence and reads the model ids from the models file in the
       path directory

    """
    model_ids = []
    try:
        with open("%s%smodels" % (path, os.sep)) as models_file:
            for line in models_file:
                model = line.strip()
                try:
                    model_id = bigml.api.get_model_id(model)
                    model_ids.append(model_id)
                except ValueError:
                    return False, model_ids
        if len(model_ids) == number_of_models:
            return True, model_ids
        else:
            return False, model_ids
    except IOError:
        return False, model_ids


def are_predictions_created(predictions_file, number_of_tests):
    """Checks existence and reads the predictions from the predictions file in
       the path directory

    """
    predictions = file_number_of_lines(predictions_file)
    if predictions != number_of_tests:
        os.remove(predictions_file)
        return False, None
    return True, None


def is_evaluation_created(path):
    """Checks existence and reads the evaluation id from the evaluation file
       in the path directory

    """
    evaluation_id = None
    try:
        with open("%s%sevaluation" % (path, os.sep)) as evaluation_file:
            evaluation_id = evaluation_file.readline().strip()
            try:
                evaluation_id = bigml.api.get_evaluation_id(evaluation_id)
                return True, evaluation_id
            except ValueError:
                return False, None
    except IOError:
        return False, None


def are_evaluations_created(path, number_of_evaluations):
    """Checks existence and reads the evaluation ids from the evaluations file
       in the path directory and checks the corresponding evaluations

    """
    evaluation_ids = []
    try:
        with open("%s%sevaluations" % (path, os.sep)) as evaluations_file:
            for line in evaluations_file:
                evaluation = line.strip()
                try:
                    evaluation_id = bigml.api.get_evaluation_id(evaluation)
                    evaluation_ids.append(evaluation_id)
                except ValueError:
                    return False, evaluation_ids
        if len(evaluation_ids) == number_of_evaluations:
            return True, evaluation_ids
        else:
            return False, evaluation_ids
    except IOError:
        return False, evaluation_ids


def are_ensembles_created(path, number_of_ensembles):
    """Checks and reads the ensembles ids from the ensembles file in the
       path directory

    """
    ensemble_ids = []
    try:
        with open("%s%sensembles" % (path, os.sep)) as ensembles_file:
            for line in ensembles_file:
                ensemble = line.strip()
                try:
                    ensemble_id = bigml.api.get_ensemble_id(ensemble)
                    ensemble_ids.append(ensemble_id)
                except ValueError:
                    return False, ensemble_ids
        if len(ensemble_ids) == number_of_ensembles:
            return True, ensemble_ids
        else:
            return False, ensemble_ids
    except IOError:
        return False, ensemble_ids


def checkpoint(function, *args, **kwargs):
    """Redirects to each checkpoint function

    """
    common_parms = ['debug', 'message', 'log_file', 'console']
    debug = kwargs.get('debug', False)
    message = kwargs.get('message', None)
    log_file = kwargs.get('log_file', None)
    console = kwargs.get('console', False)

    f_kwargs = {key: value for key, value in kwargs.items()
                if not key in common_parms}

    result = function(*args, **f_kwargs)
    if debug:
        console_log("Checkpoint: checking %s with args:\n%s\n\nResult:\n%s\n" %
                    (function.__name__, "\n".join([repr(arg) for arg in args]),
                     repr(result)))
    # resume is the first element in the result tuple
    if not result[0] and message is not None:
        log_message(message, log_file=log_file, console=console)
    return result


def file_number_of_lines(file_name):
    """Counts the number of lines in a file

    """
    try:
        item = (0, None)
        with open(file_name) as file_handler:
            for item in enumerate(file_handler):
                pass
        return item[0] + 1
    except IOError:
        return 0


def is_batch_prediction_created(path):
    """Checks existence and reads the batch prediction id from the
       batch_prediction file in the path directory

    """
    batch_prediction_id = None
    try:
        with open("%s%sbatch_prediction"
                  % (path, os.sep)) as batch_prediction_file:
            batch_prediction_id = batch_prediction_file.readline().strip()
            try:
                batch_prediction_id = bigml.api.get_batch_prediction_id(
                    batch_prediction_id)
                return True, batch_prediction_id
            except ValueError:
                return False, None
    except IOError:
        return False, None


def is_batch_centroid_created(path):
    """Checks existence and reads the batch centroid id from the
       batch_centroid file in the path directory

    """
    batch_centroid_id = None
    try:
        with open("%s%sbatch_centroid"
                  % (path, os.sep)) as batch_prediction_file:
            batch_centroid_id = batch_prediction_file.readline().strip()
            try:
                batch_centroid_id = bigml.api.get_batch_centroid_id(
                    batch_centroid_id)
                return True, batch_centroid_id
            except ValueError:
                return False, None
    except IOError:
        return False, None


def are_clusters_created(path, number_of_clusters):
    """Checks existence and reads the cluster ids from the clusters file in the
       path directory

    """
    cluster_ids = []
    try:
        with open("%s%sclusters" % (path, os.sep)) as clusters_file:
            for line in clusters_file:
                cluster = line.strip()
                try:
                    cluster_id = bigml.api.get_cluster_id(cluster)
                    cluster_ids.append(cluster_id)
                except ValueError:
                    return False, cluster_ids
        if len(cluster_ids) == number_of_clusters:
            return True, cluster_ids
        else:
            return False, cluster_ids
    except IOError:
        return False, cluster_ids


def is_dataset_exported(filename):
    """Checks the existence of the CSV exported dataset file

    """
    try:
        with open(filename):
            return True
    except IOError:
        return False


def is_batch_anomaly_score_created(path):
    """Checks existence and reads the batch anomaly score id from the
       batch_anomaly_score file in the path directory

    """
    batch_anomaly_score_id = None
    try:
        with open("%s%sbatch_anomaly_score"
                  % (path, os.sep)) as batch_prediction_file:
            batch_anomaly_score_id = batch_prediction_file.readline().strip()
            try:
                batch_anomaly_score_id = bigml.api.get_batch_anomaly_score_id(
                    batch_anomaly_score_id)
                return True, batch_anomaly_score_id
            except ValueError:
                return False, None
    except IOError:
        return False, None


def are_anomalies_created(path, number_of_anomalies):
    """Checks existence and reads the anomaly detector ids from the
       anomalies file in the path directory

    """
    anomaly_ids = []
    try:
        with open("%s%sanomalies" % (path, os.sep)) as anomalies_file:
            for line in anomalies_file:
                anomaly = line.strip()
                try:
                    anomaly_id = bigml.api.get_anomaly_id(anomaly)
                    anomaly_ids.append(anomaly_id)
                except ValueError:
                    return False, anomaly_ids
        if len(anomaly_ids) == number_of_anomaly:
            return True, anomaly_ids
        else:
            return False, anomaly_ids
    except IOError:
        return False, anomaly_ids
