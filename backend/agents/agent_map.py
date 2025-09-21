class AgentMap:
    def __init__(self):
        prompt_list = [
            # Stage 0: Tutorial
            "tutorial:latest",

            # Stage 1: Getting Started - Big Idea
            "big_idea:latest",
            "working_title:latest",
            "genre:latest",
            "main_vibe:latest",
            "one_sentence_pitch:latest",

            # Stage 2: Worldbuilding Basics
            "setting:latest",
            "time_period:latest",
            "map:latest",
            "environment:latest",
            "magic_exist:latest",

            # Stage 3: Worldbuilding Expanded
            "magic_rules:latest",
            "history:latest",
            "cultures:latest",
            "government:latest",
            "everyday_life:latest",
            "creatures:latest",
            "plants_resources:latest",

            # Stage 4: Characters
            "hero:latest",
            "hero_goal:latest",
            "hero_obstacle:latest",
            "villain:latest",
            "villain_motive:latest",
            "ally:latest",
            "other_chars:latest",
            "char_secrets:latest",

            # Stage 5: Plot Basics
            "story_shape:latest",
            "inciting_incident:latest",
            "turning_point1:latest",
            "midpoint:latest",
            "turning_point2:latest",
            "climax:latest",
            "resolution:latest",

            # Stage 6: Plot Expanded
            "stakes:latest",
            "theme:latest",
            "subplots:latest",
            "foreshadowing:latest",
            "scene_list:latest",

            # Stage 7: Writing Style
            "pov:latest",
            "tone:latest",
            "audience:latest",
            "length_goal:latest",
            "sample_para:latest"
        ]
        agent_map = {}
        i = 0  # Start from 0 instead of 1
        for prompt in prompt_list:
            agent_map[i] = prompt
            i = i + 1
        self.stage_map = agent_map

    def get_prompt(self, stage: int):
        return self.stage_map[stage]

