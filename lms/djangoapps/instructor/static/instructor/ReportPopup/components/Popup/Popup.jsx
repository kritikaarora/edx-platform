import * as React from 'react';
import * as PropTypes from 'prop-types';
import {Button} from '@edx/paragon';
import {PopupModal} from './PopupModal';

export default class Popup extends React.Component {
    constructor(props) {
        super(props);
        this.showPopup = this.showPopup.bind(this);
        this.hidePopup = this.hidePopup.bind(this);
        this.state = {
            popupOpen: false,
            taskForBlock: null,
        };
    }

    showPopup() {
        if (this.state.taskForBlock != this.props.selectedBlock) {
            this.props.createProblemResponsesReportTask(this.props.initialEndpoint, this.props.taskStatusEndpoint, this.props.selectedBlock);
        }
        this.setState({popupOpen: true, taskForBlock: this.props.selectedBlock});
    }

    hidePopup() {
        if (this.props.timeout != null) {
            clearTimeout(this.props.timeout);
        }
        this.setState({popupOpen: false, taskForBlock: null});
    }

    render() {
        return (
            <div>
                <Button onClick={this.showPopup}
                        name="list-problem-responses-csv" label={gettext("Create a report of problem responses")}
                />
                <PopupModal open={this.state.popupOpen} onHide={this.hidePopup} {...this.props}/>
            </div>
        );
    }
}

Popup.propTypes = {
    initialEndpoint: PropTypes.string.isRequired,
    taskStatusEndpoint: PropTypes.string.isRequired,
    selectedBlock: PropTypes.string.isRequired,
    createProblemResponsesReportTask: PropTypes.func.isRequired,

    timeout: PropTypes.number,
};
