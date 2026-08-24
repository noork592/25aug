#====================================================================================================
# START - Testing Protocol - DO NOT EDIT OR REMOVE THIS SECTION
#====================================================================================================

# THIS SECTION CONTAINS CRITICAL TESTING INSTRUCTIONS FOR BOTH AGENTS
# BOTH MAIN_AGENT AND TESTING_AGENT MUST PRESERVE THIS ENTIRE BLOCK

# Communication Protocol:
# If the `testing_agent` is available, main agent should delegate all testing tasks to it.
#
# You have access to a file called `test_result.md`. This file contains the complete testing state
# and history, and is the primary means of communication between main and the testing agent.
#
# Main and testing agents must follow this exact format to maintain testing data. 
# The testing data must be entered in yaml format Below is the data structure:
# 
## user_problem_statement: {problem_statement}
## backend:
##   - task: "Task name"
##     implemented: true
##     working: true  # or false or "NA"
##     file: "file_path.py"
##     stuck_count: 0
##     priority: "high"  # or "medium" or "low"
##     needs_retesting: false
##     status_history:
##         -working: true  # or false or "NA"
##         -agent: "main"  # or "testing" or "user"
##         -comment: "Detailed comment about status"
##
## frontend:
##   - task: "Task name"
##     implemented: true
##     working: true  # or false or "NA"
##     file: "file_path.js"
##     stuck_count: 0
##     priority: "high"  # or "medium" or "low"
##     needs_retesting: false
##     status_history:
##         -working: true  # or false or "NA"
##         -agent: "main"  # or "testing" or "user"
##         -comment: "Detailed comment about status"
##
## metadata:
##   created_by: "main_agent"
##   version: "1.0"
##   test_sequence: 0
##   run_ui: false
##
## test_plan:
##   current_focus:
##     - "Task name 1"
##     - "Task name 2"
##   stuck_tasks:
##     - "Task name with persistent issues"
##   test_all: false
##   test_priority: "high_first"  # or "sequential" or "stuck_first"
##
## agent_communication:
##     -agent: "main"  # or "testing" or "user"
##     -message: "Communication message between agents"

# Protocol Guidelines for Main agent
#
# 1. Update Test Result File Before Testing:
#    - Main agent must always update the `test_result.md` file before calling the testing agent
#    - Add implementation details to the status_history
#    - Set `needs_retesting` to true for tasks that need testing
#    - Update the `test_plan` section to guide testing priorities
#    - Add a message to `agent_communication` explaining what you've done
#
# 2. Incorporate User Feedback:
#    - When a user provides feedback that something is or isn't working, add this information to the relevant task's status_history
#    - Update the working status based on user feedback
#    - If a user reports an issue with a task that was marked as working, increment the stuck_count
#    - Whenever user reports issue in the app, if we have testing agent and task_result.md file so find the appropriate task for that and append in status_history of that task to contain the user concern and problem as well 
#
# 3. Track Stuck Tasks:
#    - Monitor which tasks have high stuck_count values or where you are fixing same issue again and again, analyze that when you read task_result.md
#    - For persistent issues, use websearch tool to find solutions
#    - Pay special attention to tasks in the stuck_tasks list
#    - When you fix an issue with a stuck task, don't reset the stuck_count until the testing agent confirms it's working
#
# 4. Provide Context to Testing Agent:
#    - When calling the testing agent, provide clear instructions about:
#      - Which tasks need testing (reference the test_plan)
#      - Any authentication details or configuration needed
#      - Specific test scenarios to focus on
#      - Any known issues or edge cases to verify
#
# 5. Call the testing agent with specific instructions referring to test_result.md
#
# IMPORTANT: Main agent must ALWAYS update test_result.md BEFORE calling the testing agent, as it relies on this file to understand what to test next.

#====================================================================================================
# END - Testing Protocol - DO NOT EDIT OR REMOVE THIS SECTION
#====================================================================================================



#====================================================================================================
# Testing Data - Main Agent and testing sub agent both should log testing data below this section
#====================================================================================================

user_problem_statement: "Restored a JK Products backup. User reports 'Customer not found' error when clicking 'Save all' on the Daily Report / Dispatch Report page (saving GR number, GR date, bill amount, private mark, no. of bags for a dispatched party). This blocks saving slip metadata."

backend:
  - task: "PATCH /customers/{cid} returns false 'Customer not found' for restored customers"
    implemented: true
    working: true
    file: "backend/server.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
        -working: false
        -agent: "user"
        -comment: "User reported 'Customer not found' toast on Save all in Daily/Dispatch Report after restoring a backup."
        -working: "NA"
        -agent: "main"
        -comment: "ROOT CAUSE: endpoint used find_one({'id':cid},{'_id':0,'bill_number_mode':1}) then 'if not existing'. Restored/older customer docs lack the bill_number_mode field, so the projection returns an empty dict {} which is falsy -> false 404 for a customer that actually exists. FIX: changed check to 'if existing is None'. Also applied the same fix to GET /customers/{cid}/blocked-items (blocked_items projection). Please verify saving private_mark via PATCH /customers/{cid} now succeeds for a real customer (e.g. customer_id e22aeb9d-4ce2-4955-8fed-c6bcd5343773 'HARI OM AUTO MOBILES'), and that a genuinely missing customer id still returns 404."
        -working: true
        -agent: "testing"
        -comment: "VERIFIED: All 5 test scenarios passed. (1) Admin login successful with token. (2) PATCH /customers/e22aeb9d-4ce2-4955-8fed-c6bcd5343773 with private_mark='aaaa' returned 200 with customer data (HARI OM AUTO MOBILES). (3) Full 'Save all' sequence for dispatch slip_no 288 completed successfully: GET dispatch by slip (200), PATCH dispatch with GR details (200), PATCH customer with private_mark (200), PATCH dispatch with bag_count (200). (4) PATCH /customers/00000000-0000-0000-0000-000000000000 correctly returned 404 'Customer not found'. (5) GET /customers/e22aeb9d-4ce2-4955-8fed-c6bcd5343773/blocked-items returned 200. Bug fix confirmed working - the projection-falsy issue is resolved."

metadata:
  created_by: "main_agent"
  version: "1.0"
  test_sequence: 1
  run_ui: false

test_plan:
  current_focus:
    - "PATCH /customers/{cid} returns false 'Customer not found' for restored customers"
  stuck_tasks: []
  test_all: false
  test_priority: "high_first"

agent_communication:
    -agent: "main"
    -message: "NEW: Restrict demo user JK1 from the Users management area. Added backend guard require_users_admin (blocks username in DEMO_USERNAMES={'JK1'}) applied to GET /api/users, POST /api/users, PATCH /api/users/{uid}/otp, DELETE /api/users/{uid}, POST /api/users/{uid}/reset-password, PATCH /api/users/{uid}/permissions. Please TEST: (1) login as JK1 — need its password; if unknown, an admin can reset it, but simplest: login as 'admin'/'admin123' (real admin) and confirm GET /api/users returns 200 with the user list (regression, admin must still work). (2) For JK1: since password may be unknown, ALSO verify via a JK1 token if obtainable; the key assertion is that GET /api/users returns 403 'Not permitted for this account' for username JK1 and 200 for a normal admin. If you cannot log in as JK1, set JK1's password using admin reset-password endpoint (POST /api/users/{jk1_id}/reset-password with a known password), then login as JK1 and assert GET /api/users => 403, POST /api/users => 403, DELETE /api/users/{someid} => 403. (3) Confirm normal admin (admin/admin123) still gets 200 on all these. (4) Regression: the earlier estimate endpoints and PATCH /customers fix still work. JK1 user id can be found from the admin GET /api/users list (username 'JK1')."

backend:
  - task: "Restrict demo user JK1 from Users management endpoints"
    implemented: true
    working: "NA"
    file: "backend/server.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
        -working: "NA"
        -agent: "main"
        -comment: "Added require_users_admin dependency; applied to /users list/create/otp/delete/reset-password/permissions. JK1 (admin role) must get 403; normal admin must still get 200." Added backend endpoints in server.py: POST /api/estimates (compute + persist a record, assigns a globally-unique sequential estimate_no via next_estimate_no() using db.counters _id=estimate_no, guarded against drift like next_slip_no), GET /api/estimates (list all saved, newest first, optional q filter by customer name or estimate number), GET /api/estimates/{id} (full record), DELETE /api/estimates/{id} (admin only). Existing POST /api/estimates/compute (no writes) is unchanged in behaviour. Please TEST: (1) admin login (admin/admin123). (2) POST /api/estimates with a valid customer_id (use e22aeb9d-4ce2-4955-8fed-c6bcd5343773 HARI OM AUTO MOBILES) and items list e.g. [{item_id?, item_name, quantity}] — you can first GET /api/items to grab a real item_id — expect 200 with an estimate_no. (3) Save TWO estimates and confirm estimate_no strictly increments and is UNIQUE. (4) GET /api/estimates returns them newest-first with summary fields (estimate_no, customer_name, item_count, grand_total). (5) GET /api/estimates/{id} returns the full saved breakdown. (6) GET /api/estimates?q=<customer name> and ?q=<number> filter correctly. (7) DELETE /api/estimates/{id} as admin returns ok; as non-admin (user/user123) should be 403. (8) After delete, next saved estimate must NOT reuse the deleted number (counter is increment-only). (9) POST /api/estimates with a non-existent customer_id returns 404. Note: this is a backend addition; the previously fixed PATCH /customers bug should remain working."

backend:
  - task: "Estimate records with unique sequential estimate numbers"
    implemented: true
    working: "NA"
    file: "backend/server.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
        -working: "NA"
        -agent: "main"
        -comment: "Added POST /api/estimates (save + unique estimate_no), GET /api/estimates (list), GET /api/estimates/{id}, DELETE /api/estimates/{id}. Counter estimate_no in db.counters mirrors next_slip_no drift-guard. Needs testing for uniqueness, increment-only behaviour, list/get/delete and auth."
    -agent: "testing"
    -message: "Testing complete. All 5 test scenarios PASSED. The bug fix is working correctly: (1) PATCH /customers/{cid} now returns 200 for existing restored customers (tested with e22aeb9d-4ce2-4955-8fed-c6bcd5343773), (2) Full 'Save all' sequence for dispatch slip 288 works end-to-end, (3) Non-existent customer IDs still correctly return 404, (4) GET /customers/{cid}/blocked-items also fixed and returns 200. The projection-falsy bug (empty dict {} being falsy) has been resolved by changing the check from 'if not existing' to 'if existing is None'. No issues found."