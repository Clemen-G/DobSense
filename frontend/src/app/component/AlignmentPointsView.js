'use client'

import { SwipeableList } from 'react-swipeable-list';
import 'react-swipeable-list/dist/styles.css';
import AlignmentPointView from './AlignmentPointView';
import LabeledFrame from './LabeledFrame';

export default function AlignmentPointsView({alignmentPoints}) {
    var alignmentPointsItems = [];

    if (alignmentPoints == null || alignmentPoints.length == 0) {
        return "";
    } else {
        alignmentPointsItems = alignmentPoints.map((ap) => {
            return AlignmentPointView({ap: ap});
        });
        return  <LabeledFrame label="Alignment points">
                    <SwipeableList>
                        {alignmentPointsItems}
                    </SwipeableList>
                </LabeledFrame>;
    }
}