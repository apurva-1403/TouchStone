"""Collects all hand-authored Layer 6 event bundles (and their Layer 7 artifacts) in a fixed order."""
from events import (batch_a1_access, batch_a2_access, batch_b1_incidents, batch_b2_incidents, batch_c_projects,
                    batch_d_drift, batch_e_contradictory, batch_f_baseline)

ALL_EVENTS = (
    batch_a1_access.EVENTS + batch_a2_access.EVENTS
    + batch_b1_incidents.EVENTS + batch_b2_incidents.EVENTS
    + batch_c_projects.EVENTS
    + batch_d_drift.EVENTS
    + batch_e_contradictory.EVENTS
    + batch_f_baseline.EVENTS
)

# Follow-up tickets, extra threads and generated approval-nudge emails are merged in here
# (see events/augment.py) so the hand-authored batches stay readable.
from events import augment  # noqa: E402

augment.apply(ALL_EVENTS)

# Handover section "Event type distribution (80 events total)"
EXPECTED_TYPE_COUNTS = {
    "access_request": 20,
    "incident": 16,
    "project_decision": 13,
    "policy_drift": 13,
    "contradictory_resolution": 8,
    "routine_baseline": 10,
}
