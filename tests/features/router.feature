Feature: Graph Router Logic

  Scenario: Hallucinations detected with low iterations
    Given the iteration count is 1
    And hallucinations were found
    When the router evaluates the state
    Then the next node should be "generator"

  Scenario: Hallucinations detected with max iterations
    Given the iteration count is 3
    And hallucinations were found
    When the router evaluates the state
    Then the next node should be "__end__"

  Scenario: No hallucinations detected
    Given the iteration count is 1
    And no hallucinations were found
    When the router evaluates the state
    Then the next node should be "__end__"
