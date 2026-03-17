*** Settings ***
Library    DatabaseLibrary

*** Test Cases ***
Verify DB Connection
    Connect To Database    host=localhost    port=3306
    Should Be Equal    ${status}    connected

Verify Query Execution
    ${result}=    Execute SQL    SELECT 1
    Should Not Be Empty    ${result}
