Feature: Resume Tailoring API

  Scenario: Tailoring a resume with valid input
    Given the FastAPI application is running
    When I send a POST request to "/api/tailor" with a valid base resume and job description
    Then the response status code should be 200
    And the response should contain "draft_resume"
    And the response should contain "agent_notes"
