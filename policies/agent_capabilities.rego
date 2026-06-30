package brokered_delegation.agent_capabilities

# Agent capability policy skeleton.
# The agent must be explicitly approved for the normalized action.

default agent_action_allowed := false

agent_action_allowed if {
  input.agent.exists == true
  input.requested_action_allowed_by_agent == true
  input.agent.requires_user_delegation == true
}

agent_denied_reason := "AGENT_NOT_REGISTERED" if {
  not input.agent.exists
}

agent_denied_reason := "AGENT_ACTION_NOT_ALLOWED" if {
  input.agent.exists == true
  input.requested_action_allowed_by_agent == false
}

agent_denied_reason := "AGENT_DOES_NOT_REQUIRE_USER_DELEGATION" if {
  input.agent.exists == true
  input.agent.requires_user_delegation == false
}
