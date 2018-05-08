import React from 'react';

import {Provider} from 'react-redux';
import store from '../ProblemBrowser/data/store';
import  {Button} from '@edx/paragon';

import ProblemBrowserContainer from './components/Wrapper/ProblemBrowserContainer';

export const ReportPopup = props => (
    <Provider store={store}>
        <ProblemBrowserContainer {...props} />
    </Provider>
);
