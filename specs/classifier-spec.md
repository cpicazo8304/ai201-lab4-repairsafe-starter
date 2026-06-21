# Spec: `classify_safety_tier()`

**File:** `safety.py`
**Status:** Spec incomplete — fill in all blank fields before implementing

---

## Purpose

Determine whether a home repair question is safe to answer directly, requires a cautionary response, or should be refused with a referral to a licensed professional.

---

## Input / Output Contract

**Input:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `question` | `str` | The user's home repair question |

**Output:** `dict`

| Key | Type | Description |
|-----|------|-------------|
| `"tier"` | `str` | One of: `"safe"`, `"caution"`, `"refuse"` |
| `"reason"` | `str` | One sentence explaining why this tier was assigned |

---

## Design Decisions

*Complete the fields below before writing any code. Use your AI tool in Plan or Ask mode to help you reason through what belongs here — but the decisions are yours.*

---

### Tier definitions

*Write a one-sentence definition for each tier that is precise enough to use as part of your classification prompt. Vague definitions produce inconsistent classifications.*

**safe:**
```
A repair is considered "safe" when doing the repair doesn't require professional expertise, permit, or non-basic tools and doesn't lead to substantial damages. 
```

**caution:**
```
A repair is considered "caution" when the repair is doable for the common person but may require some knowledge, mistakes can lead to meaningful damages but no flooding/gas leaks/fires/death, and the repairs are on systems (water, electrical, etc.). Component swap at existing location.
```

**refuse:**
```
A repair is considered "refuse" when the repair requires professional knowledge and input, permissions according to laws and code, and mistakes may lead to injury, death, fires, flooding, etc. Includes any new wire run, any gas work, any wall removal without engineer sign-off, water heater replacement.
```

---

### Classification approach

*How will the LLM classify the question? Will you give it just the tier definitions, or also examples (few-shot)? Will you ask it to reason step-by-step before naming the tier, or output the tier directly?*

*Consider: what happens when a question is genuinely ambiguous — e.g., "can I replace my own outlets?" Which tier should that land in, and how does your approach handle questions at the boundary?*

```
I will use examples, but they won't be easy ones. They will have to be examples of boundary examples such as "replacing" an outlet is "caution" (no new wiring, etc.) while "adding" an outlet is "refuse". However, I will also add a reasoning step that can help with the auditing (including reasons for the answer).
```

---

### Output format

*How will the LLM communicate the tier and reason back to you? Describe the exact text format you'll ask it to use, so you can parse it reliably.*

*The format you used in Lab 3 (`Label: X / Reasoning: Y`) is a reasonable starting point, but you're not required to use it. Whatever you choose, you'll need to parse it in code — so consider how much variation the LLM might introduce and how you'll handle that.*

```
I will use the `Tier: X / Reasoning: Y` approach but flipped so `Reasoning: X / Tier: Y` since I will be asking the LLM to reason step by step so it must reason first before labeling. Having the output structured like that prevents the LLM commiting to a tier before reasoning.
```

---

### Prompt structure

*Write the actual prompt you'll use — both the system message and the user message. Don't describe it — write it. Vague prompt descriptions produce vague prompts, which produce inconsistent classifications.*

**System message:**
```
You are a safety classifier for home repair questions. Classify each question into exactly one of three tiers: safe, caution, or refuse.

safe - repair doesn't require professional expertise, permit, or non-basic tools and doesn't lead to substantial damages. 

caution -  repair is doable for the common person but may require some knowledge, mistakes can lead to meaningful damages but no flooding/gas leaks/fires/death, and the repairs are on systems (water, electrical, etc.). Component swap at existing location.

refuse - repair requires professional knowledge and input, permissions according to laws and code, and mistakes may lead to injury, death, fires, flooding, etc. Includes any new wire run, any gas work, any wall removal without engineer sign-off, water heater replacement.

Return your answer in this exact format:
    Reason: <one sentence>\n
    Tier: <one of: safe, caution, refuse>

```

**User message:**
```
Here are some examples:
    {safe example}
    {caution example}
    {refuse example}
Please classify this question: {Question}.
Please think step by step before classifying. 
```

---

### Caution/refuse boundary

*The most consequential classification decision is whether a question lands in "caution" or "refuse." Write down your rule for this boundary — one sentence. Then give two examples of questions that sit close to the line and explain which side they fall on and why.*

```
If the repair does have meaningful costs for mistakes but not as serious as flooding/fires/death/gas leaks/injury then it is considered "caution". If it does includes those serious costs, then it is considered "refuse".

Examples:
    "How do I replace an outlet that stopped working?" → caution
    Don't have to change wiring and are replacing in place.

    "How do I add a new outlet to my garage?" → refuse
    Requires running a new circuit, a permit, and wiring, which could be dangerous for the common people.
    
```

---

### Fallback behavior

*What does your function return if the LLM response can't be parsed — e.g., if it produces free-form prose instead of your expected format? What happens when tier validation against `VALID_TIERS` fails?*

*Note: failing open (returning "safe" as a fallback) is more dangerous than failing closed (returning "caution"). Which makes more sense here, and why?*

```
If the tier validation fails, have to give it a "unknown" label. If a LLM response can't be parsed, then the default is reason -> "text.strip()".
```

---

## Implementation Notes

*Fill this in after implementing, before moving to Milestone 2.*

**One classification that surprised you — question, tier you expected, tier it returned, and why:**

```
Everything worked how I thought it should have.
```

**One prompt change you made after seeing the first few outputs, and what it fixed:**

```
Having the examples in the system prompt made me fail the GFCI example, but moving them to the user prompt made everything correct.
```
