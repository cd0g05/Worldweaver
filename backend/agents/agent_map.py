class AgentMap:
    def __init__(self):
        prompt_list = [
            # Stage 1: Getting Started
            "big_idea:1",
            "working_title:1",
            "genre:1",
            "main_vibe:1",
            "one_sentence_pitch:1",

            # Stage 2: Worldbuilding Basics
            "setting:1",
            "time_period:1",
            "map:1",
            "environment:1",
            "magic_exist:1",

            # Stage 3: Worldbuilding Expanded
            "magic_rules:1",
            "history:1",
            "cultures:1",
            "government:1",
            "everyday_life:1",
            "creatures:1",
            "plants_resources:1",

            # Stage 4: Characters
            "hero:1",
            "hero_goal:1",
            "hero_obstacle:1",
            "villain:1",
            "villain_motive:1",
            "ally:1",
            "other_chars:1",
            "char_secrets:1",

            # Stage 5: Plot Basics
            "story_shape:1",
            "inciting_incident:1",
            "turning_point1:1",
            "midpoint:1",
            "turning_point2:1",
            "climax:1",
            "resolution:1",

            # Stage 6: Plot Expanded
            "stakes:1",
            "theme:1",
            "subplots:1",
            "foreshadowing:1",
            "scene_list:1",

            # Stage 7: Writing Style
            "pov:1",
            "tone:1",
            "audience:1",
            "length_goal:1",
            "sample_para:1"
        ]
        agent_map = {}
        i = 1
        for prompt in prompt_list:
            agent_map[i] = prompt
            i = i + 1
        self.stage_map = agent_map

    def get_prompt(self, stage: int):
        return self.stage_map[stage]

