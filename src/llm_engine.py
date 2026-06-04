import os
import json
import anthropic
from pathlib import Path


def load_prompt(prompt_file: str) -> str:
    """Load a system prompt from the prompts directory."""
    prompt_path = Path(__file__).parent.parent / "prompts" / prompt_file
    with open(prompt_path, "r") as f:
        return f.read().strip()


def analyze_campaigns(campaign_json: str, api_key: str) -> dict:
    """
    Send campaign data to Claude API and get structured analysis.
    Returns parsed JSON dict with full analysis.
    """
    client = anthropic.Anthropic(api_key=api_key)
    system_prompt = load_prompt("analysis_system_prompt.txt")

    user_message = f"""Please analyze the following digital marketing campaign data and provide detailed insights, 
identify underperformers, flag anomalies, and give specific optimization recommendations.

Campaign Data:
{campaign_json}

Remember: Return ONLY valid JSON matching the schema in your instructions."""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4000,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}],
    )

    response_text = message.content[0].text.strip()

    # Clean up any accidental markdown wrapping
    if response_text.startswith("```"):
        response_text = response_text.split("```")[1]
        if response_text.startswith("json"):
            response_text = response_text[4:]

    return json.loads(response_text)


def analyze_competitors(industry: str, campaign_summary: str, api_key: str) -> dict:
    """
    Get competitor benchmarking and strategic analysis from Claude.
    """
    client = anthropic.Anthropic(api_key=api_key)
    system_prompt = load_prompt("competitor_prompt.txt")

    user_message = f"""Industry/Brand Context: {industry}

Our Current Campaign Summary:
{campaign_summary}

Provide competitive intelligence and benchmarking analysis."""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}],
    )

    response_text = message.content[0].text.strip()
    if response_text.startswith("```"):
        response_text = response_text.split("```")[1]
        if response_text.startswith("json"):
            response_text = response_text[4:]

    return json.loads(response_text)


def generate_ad_copy(campaign_name: str, objective: str, platform: str, api_key: str) -> dict:
    """
    Generate optimized ad copy suggestions for a specific campaign.
    """
    client = anthropic.Anthropic(api_key=api_key)

    prompt = f"""You are an expert digital marketing copywriter. Generate optimized ad copy for:
Campaign: {campaign_name}
Platform: {platform}
Objective: {objective}

Return JSON with keys:
- headline_1, headline_2, headline_3 (max 30 chars each for Google; max 40 for Meta)
- description_1, description_2 (max 90 chars each)
- cta_text (call to action button text)
- targeting_suggestion (brief audience targeting recommendation)
- tone (the tone/style used)

Return ONLY valid JSON."""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}],
    )

    response_text = message.content[0].text.strip()
    if response_text.startswith("```"):
        response_text = response_text.split("```")[1]
        if response_text.startswith("json"):
            response_text = response_text[4:]

    return json.loads(response_text)
