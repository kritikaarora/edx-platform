import { combineReducers } from 'redux';
import { blocks, selectedBlock, rootBlock } from 'BlockBrowser/data/reducers';
import {
  REPORT_GENERATION_ERROR,
  REPORT_GENERATION_SUCCESS,
  REPORT_GENERATION_TIMEOUT,
} from '../actions/constants';

const popupInitialState = {
  error: null,
  inProgress: false,
  succeeded: false,
  reportPath: null,
  reportName: null,
  timeout: null,
};

export const reportStatus = (state = popupInitialState, action) => {
  switch (action.type) {
    case REPORT_GENERATION_SUCCESS:
      return {
        ...state,
        inProgress: action.inProgress,
        succeeded: action.succeeded,
        reportPath: action.reportPath,
        reportName: action.reportName,
        error: null,
      };
    case REPORT_GENERATION_ERROR:
      return { ...state, error: action.error, succeeded: false };
    case REPORT_GENERATION_TIMEOUT:
      return { ...state, timeout: action.timeout };
    default:
      return state;
  }
};

export default combineReducers({
  blocks,
  selectedBlock,
  rootBlock,
  reportStatus,
});
