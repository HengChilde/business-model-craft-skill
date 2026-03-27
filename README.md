[中文](README.zh.md) | **English**

# business-model-craft-skill

Give your AI agent real business sense. business-model-craft-skill enables any agent to analyze a company's business model using the **Business Model Canvas** framework — producing bilingual reports, structured data, and a locally previewable web page.

## The Problem It Solves

Most AI-generated business analyses share the same flaw: you finish reading and can't remember a single concrete claim.

They're full of lines like "the company is customer-centric," "faces intense market competition," and "operates a sustainable business model" — each sentence sounds plausible, but together they say nothing.

**business-model-craft-skill flips that.** It uses the Business Model Canvas as a forcing function — pushing the analysis to answer real questions: How does this company actually make money? Is the moat real or just a head start? Where are the risks nobody's talking about? The writing is modeled after Stratechery, Not Boring, and Harvard Business Review: opinionated, sourced, and worth finishing.

## The Business Model Canvas

The hardest part of building this skill wasn't the code — it was the thinking methodology behind good business analysis.

Here's the thing about how people analyze companies: staring at a company's homepage and trying to "figure it out" rarely works. What works is a framework — something that turns an open-ended essay into a structured fill-in-the-blank. That's when you start finding the interesting parts.

The Business Model Canvas is exactly that kind of tool.

Introduced in 2005 by Alexander Osterwalder — co-founder of the strategy consulting firm Strategyzer — the Canvas breaks any business down into 9 building blocks. Nine questions a company has to answer about how it operates, creates value, and makes money.

![Business Model Canvas](https://github.com/user-attachments/assets/58bbb1b6-def0-422c-b876-d0378c2347ad)

These nine blocks aren't independent. They push against each other. And as a company moves through different stages, the canvas shifts too.

I've written a deep-dive guide on how to actually use the Canvas: [Mastering the Business Model Canvas: A Deep Dive Guide](https://businessmodelcraft.com/en/blog/business-model-guide) . I also built a tool around it — [businessmodelcraft.com](https://businessmodelcraft.com) — a free canvas builder with a library of real company case studies. This skill is the next step: bringing that same methodology to AI agents.

business-model-craft-skill distills the core ideas of the Business Model Canvas, along with two years of hands-on experience building around it, into a single skill — so your agent can reason about business models the way a sharp analyst would.

---

## What It Does

**One prompt. Four outputs.**

Name a company, or let the skill pick one from today's market movers. When the conversation wraps up, you'll have:

| File | Description |
| --- | --- |
| `[slug].html` | A local case page — double-click to open, built-in Chinese / English toggle |
| `[slug].zh.md` | Chinese deep-dive: six chapters, sharp opening take, numbers with sources, real conclusions |
| `[slug].en.md` | English version, written in the style of WSJ / HBR |
| `[slug].json` | Bilingual structured BMC data, field-compatible with [businessmodelcraft.com](https://businessmodelcraft.com) |

**Research you can trust**

Every analysis is grounded in SEC filings, earnings call transcripts (Seeking Alpha), founder interviews, and reporting from WSJ and Bloomberg. Every number has a citation.

The agent also runs a mandatory AI-filler cleanup pass before saving — scrubbing the output of clichés, hollow transitions, and the kind of language that makes business writing unreadable. The goal is prose that reads like Stratechery or Not Boring, not like a generated summary.

---

## Getting Started

**Option 1: Let your agent install it**

Works with Claude Code, OpenClaw, or any agent that can read URLs. Just send it this:

```
Install this skill: https://github.com/hengchilde/business-model-craft-skill
```

**Option 2: Download manually**

Download the repo, unzip it, and tell your agent the folder path to install from.

1. Open the [repository page](https://github.com/hengchilde/business-model-craft-skill)
2. Click the green **`<> Code`** button on the right
3. Select **Download ZIP**
4. Unzip the file — that's your Skill folder

**Using the skill**

Once installed, just start a conversation with your agent. Ask it to analyze a company's business model, or explicitly tell it to use the `business-model-craft-skill`. That's it.

---

## Where Files Are Saved

Reports are saved locally. Priority order:

1. A path you specify in the conversation
2. A global output folder you've set via environment variable (`BUSINESSMODELCRAFT_OUTPUT_BASE` or `BUSINESSMODELCRAFT_OUTPUT_DIR`)
3. Default: `~/Documents/BusinessModelCraft/[slug]/`

When done, the agent will tell you the exact path and a `file://` link you can click to open.

---

## Requirements

- Python 3.8+ (for the scripts — the agent handles dependencies automatically)
- An internet connection (for research and market data)

**Optional: Alpha Vantage API Key**

The stock-picking script pulls from Google Finance and StockAnalysis by default — no key needed. Alpha Vantage is an optional fallback for candidate validation. Sign up at [alphavantage.co](https://www.alphavantage.co) with just an email address; the free tier gives you 25 requests a day. Once you have a key, ask your agent to add it to the skill config.

---

## License

MIT
