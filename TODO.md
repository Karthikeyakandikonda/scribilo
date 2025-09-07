# TODO: Fix Login/Signup and Redirect Issues

## Tasks
- [x] Fix app.py: Change url_for("main.html") to url_for("main") in login success redirect
- [x] Fix app.py: Change route from "/template/main.html" to "/main"
- [x] Fix templates/index.html: Remove e.preventDefault() from form submit event
- [x] Fix templates/index.html: Remove JavaScript message setting (fake response)
- [x] Fix templates/index.html: Add flash message display using Jinja2
- [x] Fix templates/index.html: Add hidden input for 'action' field
- [x] Fix templates/index.html: Update JavaScript to set 'action' value on toggle
- [x] Verify templates/main.html exists or create if needed
- [ ] Test the fixes: signup, login, redirect, data storage

## Notes
- The main issue was that the form wasn't submitting to the server due to JavaScript preventing default action
- Database operations in app.py are correct, but weren't triggered because no POST requests were made
- After fixes, data should store properly in users.db
