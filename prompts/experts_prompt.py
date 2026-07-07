from string import Template

EXPERTS_PROMPT = Template("""
You are building an expert council.

Problem:
$problem

Return ONLY valid JSON.

{
  "experts": [
    {
      "name": "",
      "role": "",
      "reason": ""
    }
  ]
}

Generate between 5 and 7 experts with different domains.
""")