import {problemResponsesPopupActions} from './constants';
import {initiateProblemResponsesRequest, fetchTaskStatus} from "../api/client";

const createProblemResponsesReportTask = (initialEndpoint, taskStatusEndpoint, blockId) => (dispatch) =>
    initiateProblemResponsesRequest(initialEndpoint, blockId)
        .then((response) => {
            if (response.ok) {
                return response.json();
            }
            throw new Error(response);
        })
        .then(
            json => dispatch(getTaskStatus(taskStatusEndpoint, json.task_id)),
            error => dispatch(failure(error)),
        );


const getTaskStatusSuccess = (succeeded, inProgress, message, reportPath) => ({
    type: problemResponsesPopupActions.SUCCESS,
    succeeded: succeeded,
    inProgress: inProgress,
    message: message,
    reportPath: reportPath
});

const failure = (error) => ({
    type: problemResponsesPopupActions.ERROR,
    error: error
});

const timeoutSet = (timeout) => ({
    type: problemResponsesPopupActions.TIMEOUT,
    timeout: timeout
});

const getTaskStatus = (endpoint, taskId) => (dispatch) =>
    fetchTaskStatus(endpoint, taskId)
        .then((response) => {
            if (response.ok) {
                return response.json();
            }
            throw new Error(response);
        })
        .then(
            json => {
                if (json.in_progress) {
                    const timeout = setTimeout(() => dispatch(getTaskStatus(endpoinnt, taskId)), 1000);
                    dispatch(timeoutSet(timeout));
                }
                return dispatch(getTaskStatusSuccess(json.task_state === 'SUCCESS', json.in_progress, json.message, json.task_progress.report_path));
            },
            error => dispatch(failure(error)),
        );

export {
    failure,
    createProblemResponsesReportTask,
    getTaskStatusSuccess,
    getTaskStatus
};
