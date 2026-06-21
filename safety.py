import re

from groq import Groq
from config import GROQ_API_KEY, LLM_MODEL, VALID_TIERS

_client = Groq(api_key=GROQ_API_KEY)


def classify_safety_tier(question: str) -> dict:
    """
    Classify a home repair question into one of three safety tiers.

    Uses a single Groq chat completion request with a carefully structured
    prompt. Parses the model output for `Reason:` and `Tier:` lines and
    validates the tier against VALID_TIERS.
    """

    system_prompt = (
        "You are a safety classifier for home repair questions. Classify each question "
        "into exactly one of three tiers: safe, caution, or refuse.\n\n"
        "safe - repair doesn't require professional expertise, permit, or non-basic tools "
        "and doesn't lead to substantial damages.\n\n"
        "caution - repair is doable for the common person but may require some knowledge, "
        "mistakes can lead to meaningful damages but no flooding/gas leaks/fires/death, "
        "and the repairs are on systems (water, electrical, etc.). Component swap at existing location.\n\n"
        "refuse - repair requires professional knowledge and input, permissions according "
        "to laws and code, and mistakes may lead to injury, death, fires, flooding, etc. "
        "Includes any new wire run, any gas work, any wall removal without engineer sign-off, "
        "water heater replacement.\n\n"
        "Return your answer in this exact format:\n"
        "Reason: <one sentence>\n"
        "Tier: <one of: safe, caution, refuse>"
    )

    user_prompt = (
        f"Please classify this question: {question.strip()}\n\n"
        "Here are two examples to help guide the boundary decisions:\n"
        "Question: Can I replace an electrical outlet that stopped working?\n"
        "Reason: Replacing an existing outlet is a component swap at the same location and does not require new wiring or permits.\n"
        "Tier: caution\n\n"
        "Question: Can I add a new electrical outlet to my garage?\n"
        "Reason: Adding a new outlet requires new wiring, circuit work, and likely permits, making it high-risk and better left to a licensed professional.\n"
        "Tier: refuse\n\n"
        "Now classify this question exactly as instructed above."
        "Please think step by step and be sure to follow the output format strictly."
    )

    try:
        response = _client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=180,
            temperature=0.0,
        )

        raw = getattr(response.choices[0].message, "content", "") or ""
        tier = None
        reason = ""

        for line in (raw or "").splitlines():
            stripped = line.strip()
            if not stripped:
                continue
            lower = stripped.lower()
            if lower.startswith("tier:") and tier is None:
                tier = stripped.split(":", 1)[1].strip().lower()
            elif lower.startswith("reason:") and not reason:
                reason = stripped.split(":", 1)[1].strip()

        if not tier:
            match = re.search(r"tier\s*:\s*(safe|caution|refuse)", raw, flags=re.IGNORECASE)
            if match:
                tier = match.group(1).lower()

        if not reason:
            match = re.search(r"reason\s*:\s*(.*)", raw, flags=re.IGNORECASE)
            if match:
                reason = match.group(1).strip()

        if tier not in VALID_TIERS:
            tier = "unknown"
            if not reason:
                reason = (
                    "The model response could not be parsed into a valid tier, so this question "
                    "is being treated as caution to fail safe."
                )

        if not reason:
            cleaned = re.sub(r"(?i)tier\s*:\s*(safe|caution|refuse)", "", raw)
            cleaned = re.sub(r"(?i)reason\s*:\s*", "", cleaned)
            reason = cleaned.strip() or "Could not extract a concise reason from the model response."

        return {"tier": tier, "reason": reason}
    except Exception as exc:
        return {
            "tier": "caution",
            "reason": f"LLM classification failed; defaulting to caution. Error: {exc}",
        }
