from string import Template


PLANNER_PROMPT = Template("""

You are an expert project planner.

Problem

$problem

Return ONLY JSON.

{

"objective":"",

"domain":"",

"stakeholders":[

],

"constraints":[

],

"assumptions":[

]

}

""")