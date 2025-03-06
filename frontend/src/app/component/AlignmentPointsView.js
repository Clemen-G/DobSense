'use client'

import { SwipeableList } from 'react-swipeable-list';
import 'react-swipeable-list/dist/styles.css';
import AlignmentPointView from './AlignmentPointView';
import LabeledFrame from './LabeledFrame';

export default function AlignmentPointsView({alignmentPoints}) {
    let alignmentPointsItems = [];

    if (alignmentPoints == null || alignmentPoints.length == 0) {
        return "";
    } else {
        alignmentPointsItems = alignmentPoints.map((ap) => {
            return AlignmentPointView({ap: ap});
        });
        return  <LabeledFrame label="Alignment points" classes="alignmentpointscontainer">
                    <SwipeableList>
                        {alignmentPointsItems}
                    </SwipeableList>
                </LabeledFrame>;
    }
}