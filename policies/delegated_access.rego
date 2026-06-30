package brokered_delegation

# Phase 0 policy skeleton.
# Phase 1 will wire this to config-loaded input.

default allow := false

allow if {
  input.user.exists == true
  input.agent.exists == true
  input.app.exists == true
  input.scope.exists == true
  input.user.has_requested_scope == true
  input.agent.has_requested_action == true
  input.app.accepts_requested_scope == true
  input.data_classification_allowed == true
  input.risk_tier_allowed == true
}

deny_reason contains "USER_UNKNOWN" if {
  not input.user.exists
}

deny_reason contains "AGENT_UNKNOWN" if {
  not input.agent.exists
}

deny_reason contains "TARGET_APP_UNKNOWN" if {
  not input.app.exists
}

deny_reason contains "SCOPE_UNKNOWN" if {
  not input.scope.exists
}

deny_reason contains "USER_LACKS_SCOPE" if {
  input.user.exists == true
  input.user.has_requested_scope == false
}

deny_reason contains "AGENT_LACKS_CAPABILITY" if {
  input.agent.exists == true
  input.agent.has_requested_action == false
}

deny_reason contains "TARGET_APP_DOES_NOT_ACCEPT_SCOPE" if {
  input.app.exists == true
  input.app.accepts_requested_scope == false
}

deny_reason contains "DATA_CLASSIFICATION_NOT_ALLOWED" if {
  input.data_classification_allowed == false
}

deny_reason contains "RISK_TIER_EXCEEDED" if {
  input.risk_tier_allowed == false
}
