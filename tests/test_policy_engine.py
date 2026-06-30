from brokered_delegation import evaluate_request


def test_allow_alice_create_ticket():
    decision = evaluate_request(
        {
            "request_id": "T001",
            "user": "alice@example.com",
            "agent": "support-agent-001",
            "target_app": "ticketing-api",
            "action": "ticketing.create_ticket",
            "requested_scope": "ticket:create",
        }
    )

    evidence = decision.to_evidence()
    assert evidence["policy_decision"] == "ALLOW"
    assert evidence["reason_code"] == "USER_AND_AGENT_AUTHORIZED"
    assert evidence["token_exchange"] == "SUCCESS"
    assert evidence["token_audience"] == "ticketing-api"
    assert evidence["token_scope"] == "ticket:create"
    assert evidence["raw_token_logged"] is False


def test_deny_bob_create_ticket_without_scope():
    decision = evaluate_request(
        {
            "request_id": "T002",
            "user": "bob@example.com",
            "agent": "support-agent-001",
            "target_app": "ticketing-api",
            "action": "ticketing.create_ticket",
            "requested_scope": "ticket:create",
        }
    )

    evidence = decision.to_evidence()
    assert evidence["policy_decision"] == "DENY"
    assert evidence["reason_code"] == "USER_LACKS_SCOPE"
    assert evidence["token_exchange"] == "NOT_ATTEMPTED"


def test_deny_prompt_injection_hr_salary_access():
    decision = evaluate_request(
        {
            "request_id": "T003",
            "user": "alice@example.com",
            "agent": "support-agent-001",
            "target_app": "hr-api",
            "action": "hr.read_salary",
            "requested_scope": "salary:read",
        }
    )

    evidence = decision.to_evidence()
    assert evidence["policy_decision"] == "DENY"
    assert evidence["reason_code"] in {
        "USER_LACKS_SCOPE",
        "AGENT_LACKS_CAPABILITY",
        "AGENT_NOT_ALLOWED_FOR_TARGET_APP",
    }
    assert evidence["token_exchange"] == "NOT_ATTEMPTED"


def test_deny_unknown_agent():
    decision = evaluate_request(
        {
            "request_id": "T004",
            "user": "alice@example.com",
            "agent": "unknown-agent",
            "target_app": "crm-api",
            "action": "crm.read_customer",
            "requested_scope": "customer:read",
        }
    )

    evidence = decision.to_evidence()
    assert evidence["policy_decision"] == "DENY"
    assert evidence["reason_code"] == "AGENT_UNKNOWN_OR_DISABLED"


def test_deny_unknown_target_app():
    decision = evaluate_request(
        {
            "request_id": "T005",
            "user": "alice@example.com",
            "agent": "support-agent-001",
            "target_app": "unknown-api",
            "action": "crm.read_customer",
            "requested_scope": "customer:read",
        }
    )

    evidence = decision.to_evidence()
    assert evidence["policy_decision"] == "DENY"
    assert evidence["reason_code"] == "TARGET_APP_UNKNOWN"


def test_deny_admin_scope_escalation():
    decision = evaluate_request(
        {
            "request_id": "T006",
            "user": "alice@example.com",
            "agent": "support-agent-001",
            "target_app": "admin-api",
            "action": "admin.grant_role",
            "requested_scope": "admin:grant_role",
        }
    )

    evidence = decision.to_evidence()
    assert evidence["policy_decision"] == "DENY"
    assert evidence["token_exchange"] == "NOT_ATTEMPTED"
    assert evidence["raw_token_logged"] is False


def test_evidence_contains_required_core_fields():
    evidence = evaluate_request(
        {
            "request_id": "T007",
            "user": "alice@example.com",
            "agent": "support-agent-001",
            "target_app": "knowledge-api",
            "action": "knowledge.read_runbook",
            "requested_scope": "runbook:read",
        }
    ).to_evidence()

    for key in [
        "timestamp",
        "request_id",
        "user",
        "agent",
        "target_app",
        "action",
        "requested_scope",
        "policy_decision",
        "reason_code",
        "token_exchange",
        "api_access",
        "raw_token_logged",
    ]:
        assert key in evidence
