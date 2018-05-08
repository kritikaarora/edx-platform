import {combineReducers} from 'redux';
import {problemResponsesPopupActions} from '../actions/constants';

const popupInitialState = {
    message: null,
    error: null,
    inProgress: false,
    succeeded: false,
    reportPath: null,
    timeout: null
};

export const popupTask = (state = popupInitialState, action) => {
    switch (action.type) {
        case problemResponsesPopupActions.SUCCESS:
            return {
                ...state,
                message: action.message,
                inProgress: action.inProgress,
                succeeded: action.succeeded,
                reportPath: action.reportPath,
                error: null,
            };
        case problemResponsesPopupActions.ERROR:
            return {...state, error: action.error, succeeded: false};
        case problemResponsesPopupActions.TIMEOUT:
            return {...state, timeout: action.timeout};
        default:
            return state;
    }
};
