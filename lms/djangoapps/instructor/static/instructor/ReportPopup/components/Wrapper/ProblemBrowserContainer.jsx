import {connect} from 'react-redux';

import {createProblemResponsesReportTask} from '../../data/actions/problemResponses';
import ProblemBrowserWrapper from "./ProblemBrowserWrapper";

const mapStateToProps = state => ({
    error: state.popupTask.error,
    message: state.popupTask.message,
    inProgress: state.popupTask.inProgress,
    succeeded: state.popupTask.succeeded,
    reportPath: state.popupTask.reportPath,
    timeout: state.popupTask.timeout,
    selectedBlock: state.selectedBlock,
});

const mapDispatchToProps = dispatch => ({
    createProblemResponsesReportTask: (initialEndpoint, taskStatusEndpoint, problemLocation) =>
        dispatch(createProblemResponsesReportTask(initialEndpoint, taskStatusEndpoint, problemLocation)),
});

const ProblemBrowserContainer = connect(
    mapStateToProps,
    mapDispatchToProps,
)(ProblemBrowserWrapper);

export default ProblemBrowserContainer;
