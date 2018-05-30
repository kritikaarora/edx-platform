import * as React from 'react';
import * as PropTypes from 'prop-types';
import * as classNames from 'classnames';
import {Modal, Button, Hyperlink} from '@edx/paragon/static';

export const PopupModal = ({open, onHide, message, error, inProgress, succeeded, reportPath}) => {
    const handleDownload = () => {
        window.open(`/media/${reportPath}`, '_blank');
    };

    const getButtons = () => {
        let buttons = [];

        if (reportPath != null) {
            buttons.push((
                <Button label={gettext("Download CSV")} onClick={handleDownload}/>
            ));
        }

        return buttons;
    };

    const getProgress = () => {
        let progress = null;
        if (reportPath == null) {
            if (inProgress) {
                progress = (
                    <div className={"title"}>
                        <span className={"fa fa-refresh fa-spin fa-fw"}/>
                        <b>{gettext("Your report is being created...")}</b>
                    </div>
                );
            }
        }

        return progress;
    };

    const getBody = () => {
        const progress = getProgress();
        let msg = null;
        if (error != null) {
            msg = (
                <div className="msg msg-error">{error}</div>
            );
        } else if (message != null) {
            const className = classNames('msg', {'msg-success': succeeded, 'msg-warning': !succeeded});
            msg = (
                <div
                    className={className}>{message}</div>
            );
        }

        return (
            <div className={"report-popup-modal-body"}>
                {progress}
                {msg}
                <p>
                    {gettext("Once it's ready, you can view or download it using the buttons below. You can also close " +
                    "this popup now, and download the report later, from the \"Reports Available for Download\" area " +
                    "below.")}
                </p>
            </div>
        );
    };

    return (
        <Modal title={gettext("Learner Response Report")}
               body={getBody()}
               buttons={getButtons()}
               onClose={onHide}
               open={open}
               closeText={gettext("Close")}/>
    );
};

PopupModal.propTypes = {
    open: PropTypes.bool,
    onHide: PropTypes.func.isRequired,

    message: PropTypes.string,
    error: PropTypes.string,
    inProgress: PropTypes.bool.isRequired,
    succeeded: PropTypes.bool.isRequired,
    reportPath: PropTypes.string,
};
