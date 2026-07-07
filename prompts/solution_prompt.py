from string import Template

SOLUTION_PROMPT = Template("""
You are the Chief Decision Officer of ThinkForge AI.

You have received:

Problem:
$problem

Objective:
$objective

Analysis:
$analysis

Expert Debate:
$debate

Create a COMPLETE implementation-ready solution.

Return ONLY valid JSON.

{
    "executive_summary":"",
    "technical_report":"",

    "architecture":{
        "title":"",
        "components":[]
    },

    "budget":{
        "items":[
            {
                "name":"",
                "cost":""
            }
        ],
        "total":""
    },

    "timeline":[
        {
            "phase":"",
            "duration":""
        }
    ],

    "risks":[
        {
            "risk":"",
            "mitigation":""
        }
    ],

    "kpis":[
        ""
    ],

    "implementation_plan":[
        ""
    ],

    "ppt":[
        {
            "title":"",
            "content":[]
        }
    ],

    "mermaid":""
}
""")