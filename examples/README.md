# Examples

This directory contains practical examples demonstrating various techniques and tools that can be useful when working with different types of projects.

## Available Examples

### [LuaLaTeX Font Constructor](lualatex-font-constructor/)

Demonstrates how to create custom font features in LuaLaTeX using font constructors. This example shows:
- How to modify font character properties using Lua
- How to register custom font features with the Harfbuzz renderer
- How to apply visual effects (color, spacing) to specific characters
- Integration with fontspec and babel

This technique is particularly useful for:
- Creating language-specific typographic features
- Implementing custom ligatures
- Fine-tuning character appearance and spacing

### [Uphold–Notion Kontrola](uphold-notion-kontrola/)

A Python utility that syncs live portfolio data from the **Uphold API** into a
**Notion database** with automated validation checks (*kontrola*). This example shows:
- How to authenticate with the Uphold v0 REST API
- How to upsert pages in a Notion database (create or update, no duplicates)
- How to run balance/staleness checks and surface alerts in Notion
- How to schedule the sync with cron or GitHub Actions

This technique is particularly useful for:
- Real-time crypto/fiat portfolio dashboards in Notion
- Automated alerting for low balances or held funds
- Audit trails of portfolio changes over time

## Contributing Examples

Examples should:
- Be self-contained and easy to understand
- Include clear documentation explaining what they do and why
- Provide context on when to use the technique
- Include any necessary setup or dependencies
- Be placed in their own subdirectory with a descriptive name
- Include a README.md explaining the example

## Purpose

These examples serve as reference implementations and learning resources for various techniques across different domains (LaTeX, programming languages, tools, etc.).
