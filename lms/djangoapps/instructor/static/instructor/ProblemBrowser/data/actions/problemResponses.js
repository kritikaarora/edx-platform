/* global gettext */
import { fetchTaskStatus, initiateProblemResponsesRequest } from '../api/client';
import {
  REPORT_GENERATION_ERROR,
  REPORT_GENERATION_SUCCESS,
  REPORT_GENERATION_TIMEOUT,
} from './constants';

const getTaskStatusSuccess = (succeeded, inProgress, reportPath, reportName) => ({
  type: REPORT_GENERATION_SUCCESS,
  succeeded,
  inProgress,
  reportPath,
  reportName,
});

const failure = error => ({
  type: REPORT_GENERATION_ERROR,
  error,
});

const timeoutSet = timeout => ({
  type: REPORT_GENERATION_TIMEOUT,
  timeout,
});

const getTaskStatus = (endpoint, taskId) => dispatch =>
  fetchTaskStatus(endpoint, taskId)
    .then((response) => {
      if (response.ok) {
        return response.json();
      }
      throw new Error(response);
    })
    .then(
      (statusData) => {
        if (statusData.in_progress) {
          const timeout = setTimeout(() => dispatch(getTaskStatus(endpoint, taskId)), 1000);
          dispatch(timeoutSet(timeout));
        }
        return dispatch(
          getTaskStatusSuccess(
            statusData.task_state === 'SUCCESS',
            statusData.in_progress,
            statusData.task_progress.report_path,
            statusData.task_progress.report_name,
          ));
      },
      () => dispatch(failure(gettext('Error: Unable to get report generation status.'))),
    );

const createProblemResponsesReportTask = (
  problemResponsesEndpoint,
  taskStatusEndpoint,
  blockId,
) => dispatch =>
  initiateProblemResponsesRequest(problemResponsesEndpoint, blockId)
    .then((response) => {
      if (response.ok) {
        return response.json();
      }
      throw new Error(response);
    })
    .then(
      json => dispatch(getTaskStatus(taskStatusEndpoint, json.task_id)),
      () => dispatch(failure(gettext('Error: Unable to submit request to generate report.'))),
    );


export {
  failure,
  createProblemResponsesReportTask,
  getTaskStatusSuccess,
  getTaskStatus,
};
