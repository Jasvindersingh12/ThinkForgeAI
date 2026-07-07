from string import Template

DEBATE_PROMPT = Template("""
You are moderating an expert council.

Problem:
$problem

Experts:
$experts

Each expert should debate the problem and collaborate toward one final solution.

Return ONLY valid JSON.

{
    "discussion":[
        {
            "expert":"",
            "opinion":""
        }
    ],

    "agreements":[
        ""
    ],

    "disagreements":[
        ""
    ],

    "final_consensus":"",

    "confidence":0.0
}
""")