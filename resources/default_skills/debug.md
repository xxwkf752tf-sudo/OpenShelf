---
name: debug
description: Debug an issue by analyzing logs and code
allowed_tools: [bash, file_read, grep, glob]
chain_to: []
---
# Debug Skill

Systematic debugging workflow:

1. Reproduce the issue if possible
2. Check recent changes (git log --oneline)
3. Search for relevant error messages in code and logs
4. Add strategic logging or breakpoints
5. Test hypotheses one at a time
6. Document root cause and fix

Always start with the smallest possible reproduction case.
