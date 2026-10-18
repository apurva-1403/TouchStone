"""Tiny authoring DSL for Layer 6 events and their Layer 7 artifacts.

Events and artifacts are written *by name* (people, teams, systems, policies, projects).
build.py resolves names -> IDs and refuses to build if anything doesn't exist upstream.

Text fields may contain placeholders that are resolved after IDs are assigned:
    {{ticket:EVT-050#1}}   -> ticket_id of the 1st ticket of EVT-050
    {{doc:EVT-021#1}}      -> doc_id of the 1st doc of EVT-021
    {{email:EVT-021#1}}    -> thread_id
    {{slack:EVT-021#1}}    -> conversation_id
    {{pol:<policy title>}} -> policy_id
    {{proj:<project name>}}-> project_id
"""
from __future__ import annotations


def E(id, type, subtype, date, people, team, summary, outcome, *, system=None, policy=None, project=None,
      drift=False, tickets=(), emails=(), slack=(), docs=(), related_events=(), tags=(), drift_note=None,
      demo=None):
    """An event: the connective record every artifact below it derives from."""
    return {
        "id": id, "type": type, "subtype": subtype, "date": date, "people": list(people), "team": team,
        "system": system, "policy": policy, "project": project, "summary": summary, "outcome": outcome,
        "drift": drift, "drift_note": drift_note, "tickets": list(tickets), "emails": list(emails),
        "slack": list(slack), "docs": list(docs), "related_events": list(related_events), "tags": list(tags),
        "demo": demo,
    }


def T(subject, description, resolution, requester, assignee, created, *, status="resolved", resolved=None,
      group=None, priority="P3", category="access", kind="request", sensitivity=None, on_behalf_of=None,
      approvers=(), work_notes=None):
    """ServiceNow ticket. kind: request -> RITM, incident -> INC, change -> CHG."""
    return {
        "subject": subject, "description": description, "resolution": resolution, "requester": requester,
        "assignee": assignee, "created": created, "resolved": resolved, "status": status, "group": group,
        "priority": priority, "category": category, "kind": kind, "sensitivity": sensitivity,
        "on_behalf_of": on_behalf_of, "approvers": list(approvers), "work_notes": work_notes,
    }


def M(subject, messages, *, sensitivity=None, department=None):
    """Email thread. messages: [(from_name, to, 'YYYY-MM-DDTHH:MM', body), ...]; `to` = name | DL | list."""
    return {"subject": subject, "messages": list(messages), "sensitivity": sensitivity, "department": department}


def S(channel, messages, *, sensitivity=None, private=False, department=None):
    """Slack conversation. messages: [(name, 'YYYY-MM-DDTHH:MM', text), ...]."""
    return {"channel": channel, "messages": list(messages), "sensitivity": sensitivity, "private": private,
            "department": department}


def D(title, body, *, doc_type, space, created, authors, sensitivity=None, references=(), related_events=(),
      labels=(), last_updated=None, department=None, related_systems=(), related_projects=(), related_policies=()):
    """Confluence page. references: free-text ids/placeholders this page cites.
    related_systems/projects/policies are names (resolved to IDs at build time)."""
    return {"title": title, "body": body, "doc_type": doc_type, "space": space, "created": created,
            "authors": list(authors), "sensitivity": sensitivity, "references": list(references),
            "related_events": list(related_events), "labels": list(labels), "last_updated": last_updated,
            "department": department, "related_systems": list(related_systems),
            "related_projects": list(related_projects), "related_policies": list(related_policies)}
