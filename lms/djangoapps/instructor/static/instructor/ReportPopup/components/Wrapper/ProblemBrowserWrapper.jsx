import * as React from 'react';
import * as PropTypes from 'prop-types';
import {Button} from '@edx/paragon';

import {ProblemBrowser} from '../../../ProblemBrowser';
import Popup from '../Popup/Popup';

export default class ProblemBrowserWrapper extends React.Component {
    constructor(props) {
        super(props);
    }

    render() {
        let reportPopup = null;
        if (this.props.selectedBlock != null) {
            reportPopup = (<Popup {...this.props} />);
        }

        return (
            <div>
                <ProblemBrowser courseId={this.props.courseId} excludeBlockTypes={this.props.excludeBlockTypes} />
                {reportPopup}
            </div>
        );
    }
}

ProblemBrowserWrapper.propTypes = {
    courseId: PropTypes.string.isRequired,
    excludeBlockTypes: PropTypes.arrayOf(PropTypes.string),
    selectedBlock: PropTypes.string,
    initialEndpoint: PropTypes.string.isRequired,
    taskStatusEndpoint: PropTypes.string.isRequired,
    createProblemResponsesReportTask: PropTypes.func.isRequired,
};
