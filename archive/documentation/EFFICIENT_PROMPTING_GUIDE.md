# Efficient Prompting Guide - Token Optimization

**Goal:** Get the best results with minimal token usage

---

## Quick Reference: Do's and Don'ts

### ✅ DO: Use Specific, Focused Questions

**❌ Bad (Wastes tokens):**
```
Explain how the entire project works and all the APIs and how authentication works and the database structure and error handling
```

**✅ Good (Efficient):**
```
How does the /api/auth/login endpoint authenticate users?
```

### ✅ DO: Use File References Instead of Pasting

**❌ Bad:**
```
Here's my entire app.py file:
[500 lines of code pasted]
Can you explain how it works?
```

**✅ Good:**
```
@app.py Explain the authentication flow starting at line 45
```

### ✅ DO: Use MCP Tools

**❌ Bad:**
```
Read this file content:
[entire file pasted]
```

**✅ Good:**
```
@filesystem Read and analyze: app.py
```

### ✅ DO: Ask One Thing at a Time

**❌ Bad:**
```
Fix the bugs, optimize the code, add error handling, write tests, and update documentation
```

**✅ Good:**
```
Fix the authentication bug in login() function
```

Then in next request:
```
Add error handling to the login() function
```

---

## Prompt Templates

### 1. Code Explanation (Minimal Tokens)

```
@file:startLine:endLine Explain what this code does
```

**Example:**
```
@app.py:45:78 Explain the authentication logic
```

### 2. Bug Fix Request

```
@file Fix the bug at line X that causes [specific error]
```

**Example:**
```
@app.py Fix the bug at line 123 that returns 500 when user is None
```

### 3. Feature Addition

```
@file Add [feature] to [function/class] following existing patterns
```

**Example:**
```
@app.py Add rate limiting to the login endpoint following existing patterns
```

### 4. Code Review

```
@file Review lines X-Y for potential issues
```

**Example:**
```
@app.py Review lines 100-150 for security issues
```

### 5. Refactoring

```
@file Refactor [component] to [goal] without changing functionality
```

**Example:**
```
@app.py Refactor the database connection to use connection pooling
```

---

## Token-Saving Techniques

### 1. Use Line Ranges

Instead of mentioning entire file, use specific line ranges:

```
❌ "Look at app.py" (includes entire file in context)
✅ "@app.py:45:78" (only includes relevant lines)
```

### 2. Reference Previous Context

After initial explanation, reference it instead of repeating:

```
❌ "Earlier I showed you the login function, now explain..."
✅ "Explain the logout() function using the same pattern as login()"
```

### 3. Leverage MCP Memory

Store important context in memory:

```
@memory Remember: This project uses Flask, PostgreSQL, and JWT auth
```

Then later:
```
Add a new endpoint using our existing auth pattern
```

### 4. Break Complex Tasks into Steps

**❌ Single massive request:**
```
Refactor the entire authentication system to use OAuth, add rate limiting, implement refresh tokens, update tests, and create migration scripts
```

**✅ Sequential requests:**
```
Step 1: Add OAuth support to existing auth system
Step 2: [After step 1] Add rate limiting to OAuth endpoints
Step 3: [After step 2] Implement refresh token rotation
```

### 5. Use Composer for Multi-File Edits

For multiple related files, use Composer instead of chat:

```
❌ Chat: "Update app.py, config.py, and utils.py to..."
✅ Composer (Ctrl+I): "Update authentication across all files to use new pattern"
```

---

## Model Selection Strategy

### Use GPT-3.5/Gemini Flash For:
- ✅ Simple code explanations
- ✅ Basic refactoring
- ✅ Linting fixes
- ✅ Documentation updates
- ✅ Simple bug fixes

**Prompt Example:**
```
[Simple task] - Use fast model
```

### Use Default/Composer For:
- ✅ Multi-file changes
- ✅ Complex refactoring
- ✅ Architecture decisions
- ✅ Test generation

**Prompt Example:**
```
[Complex task] - Use Composer
```

### Reserve Claude Sonnet For:
- ⚠️ Only truly complex problems
- ⚠️ Architecture redesigns
- ⚠️ Critical security reviews

**Prompt Example:**
```
[Critical/Complex task] - Use Sonnet
```

---

## Context Management

### When Starting Fresh:

1. **Use @memory** to set context:
```
@memory Remember: This is a Python Flask crypto data aggregator with FastAPI endpoints
```

2. **Then ask specific questions:**
```
How can we optimize the OHLCV data fetching?
```

### When Continuing Conversation:

1. **Reference previous context:**
```
Following the authentication pattern we discussed, add logout endpoint
```

2. **Use @memory to recall:**
```
@memory What patterns did we establish for error handling?
```

---

## Common Patterns

### Pattern 1: Explain → Modify → Test

**Step 1:**
```
@app.py:100:150 Explain the error handling pattern
```

**Step 2:**
```
Apply the same pattern to the new endpoint at line 200
```

**Step 3:**
```
Write a test for the new endpoint following existing test patterns
```

### Pattern 2: Search → Review → Fix

**Step 1:**
```
@codebase Find all instances of SQL injection vulnerabilities
```

**Step 2:**
```
Review each instance and prioritize fixes
```

**Step 3:**
```
Fix the highest priority issue first
```

### Pattern 3: Generate → Refine → Integrate

**Step 1:**
```
Generate a helper function for API rate limiting
```

**Step 2:**
```
Refine it to match our project's error handling style
```

**Step 3:**
```
Integrate it into the existing middleware system
```

---

## Token Budget Per Request

### Simple Requests (< 5,000 tokens):
- Code explanation (single function)
- Simple bug fixes
- Documentation updates
- Single-file edits

### Medium Requests (5,000-15,000 tokens):
- Multi-file refactoring
- Feature additions
- Test generation
- Code reviews

### Complex Requests (15,000+ tokens):
- Architecture changes
- Security audits
- Large-scale refactoring

**Note:** With optimizations, most requests should be < 8,000 tokens

---

## Anti-Patterns to Avoid

### ❌ DON'T: Paste Large Code Blocks

```
❌ Here's my entire 1000-line file...
✅ @file Analyze the authentication module
```

### ❌ DON'T: Ask Multiple Unrelated Questions

```
❌ How does auth work? Also fix the database bug. And explain the API structure.
✅ How does authentication work? [Wait for response]
```

### ❌ DON'T: Repeat Context

```
❌ "As I mentioned earlier, the project uses Flask. The project uses Flask for..."
✅ "Using our Flask setup, explain..."
```

### ❌ DON'T: Use Vague Descriptions

```
❌ "Fix the broken thing"
✅ "Fix the TypeError in login() at line 123 when username is None"
```

### ❌ DON'T: Request Everything at Once

```
❌ "Refactor everything, add tests, fix bugs, optimize, and document"
✅ "Refactor the authentication module" [Then continue incrementally]
```

---

## Quick Tips

1. **Start narrow, expand if needed** - Begin with specific questions
2. **Use @file references** - Don't paste code
3. **Leverage MCP tools** - Filesystem, memory, database queries
4. **Break complex tasks** - One thing at a time
5. **Reference previous context** - Don't repeat explanations
6. **Use appropriate model** - Fast for simple, Composer for complex
7. **Clear chat when switching topics** - Start fresh conversations
8. **Store context in memory** - Use @memory for persistent knowledge

---

## Example Efficient Workflow

### Task: Add rate limiting to API

**Inefficient Approach (High Tokens):**
```
Here's my entire app.py with 800 lines. Here's the config. Here's the requirements. 
Please add rate limiting to all endpoints, handle errors properly, add tests, update 
documentation, and make it configurable. Also explain how it works.
```
**Tokens:** ~50,000+

**Efficient Approach (Low Tokens):**
```
Step 1: @app.py Show me the existing middleware pattern
Step 2: Add rate limiting middleware following the existing pattern
Step 3: Apply it to the authentication endpoints
Step 4: @tests Write a test for rate limiting
```
**Tokens:** ~8,000 total

**Savings:** 84% reduction

---

## Checklist Before Sending

Before sending a prompt, ask:

- [ ] Is this the most specific version of my question?
- [ ] Am I using @file instead of pasting code?
- [ ] Can I use an MCP tool instead?
- [ ] Am I asking one thing at a time?
- [ ] Am I using the right model for the task?
- [ ] Can I reference previous context instead of repeating?
- [ ] Is this the right tool (chat vs composer)?

---

**Remember:** Better prompts = Better results + Fewer tokens

