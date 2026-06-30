package brokered_delegation.data_classification

# Data classification policy skeleton.
# Phase 1 will map user clearance and agent allowed classifications from config.

default classification_allowed := false

classification_allowed if {
  input.user_clearance_allows_data == true
  input.agent_allows_data == true
}

classification_denied_reason contains "USER_CLEARANCE_TOO_LOW" if {
  input.user_clearance_allows_data == false
}

classification_denied_reason contains "AGENT_CLASSIFICATION_NOT_ALLOWED" if {
  input.agent_allows_data == false
}
