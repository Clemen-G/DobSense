'use client'

import axios from 'axios';
import { SwipeableListItem, SwipeAction, TrailingActions } from "react-swipeable-list"
import { appContext } from '../appContext.js';

export default function AlignmentPointView({ap}) {
    function delete_ap(alignment_point_id) {
        axios.delete('/api/alignments/'+alignment_point_id)
        .then(function (response) {
          console.log("alignment point deleted");
        })
        .catch(function (error) {
          appContext.apiErrorHandler(error);
        });
    }

    // converts an epoch timestamp to local time hh:mm
    function epoch_to_local_time(epoch) {
        const d = new Date(0);
        d.setUTCSeconds(epoch);
        return d.toLocaleTimeString('en-US', { hour12: false, hour: "numeric", minute: "numeric"});
    }

    function trailingActions(ap_id) {
        return <TrailingActions>
          <SwipeAction
            destructive={false}
            onClick={() => delete_ap(ap_id)}>
            Delete
          </SwipeAction>
        </TrailingActions>
    };

    function state_to_char(state) {
        if (state === "candidate") {
            return "+";
        } else if (state === "deleting") {
            return "-";
        } else {
            return "✔";
        }
    }
    return <SwipeableListItem
            key={ap.id}
            trailingActions={trailingActions(ap.id)}>
            <div>{state_to_char(ap.state)} {ap.object_id} {epoch_to_local_time(ap.timestamp)}</div>
          </SwipeableListItem>
}