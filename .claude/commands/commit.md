---
allowed-tools: Bash(git:*), Read, Grep
argument-hint: [optional custom message or flags]
description: Analyze git changes and create comprehensive commit message
model: claude-sonnet-4-20250514
---

# Intelligent Git Commit Generator

I'll analyze your current git changes and automatically create a comprehensive commit with a professional message following best practices.

## Step 1: Analysis

Let me examine the current git status and staged changes:

!git status --porcelain

Now let me analyze the staged changes in detail:

!git diff --staged

And check recent commit history for context and style consistency:

!git log --oneline -10

## Step 2: Change Classification

Based on the analysis, I'll identify:

1. **Scope of Changes**: Which files and components were modified
2. **Type of Changes**: feature, fix, refactor, docs, style, test, or chore
3. **Impact Assessment**: Significance and potential breaking changes
4. **Related Context**: Dependencies and related files

## Step 3: Commit Message Generation

I'll generate a commit message following conventional commit format:

```
<type>[optional scope]: <description>

[optional body explaining what and why vs how]

[optional footer for breaking changes, issues, etc.]
```

### Commit Types:
- **feat**: New feature for users
- **fix**: Bug fix for users  
- **docs**: Documentation changes
- **style**: Code style changes (formatting, semicolons, etc.)
- **refactor**: Code restructuring without behavior changes
- **test**: Adding or updating tests
- **chore**: Maintenance tasks, dependency updates

## Step 4: Execute Commit

I'll now execute the git commit with the generated message:

!git commit -m "$(cat <<'EOF'
[Generated commit message will appear here]

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"

## Step 5: Verification

Finally, I'll verify the commit was successful:

!git status
!git log --oneline -1

Arguments: $ARGUMENTS