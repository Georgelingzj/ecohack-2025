from simulator.agents import BaseAgent

from simulator.types import EnvironmentModel, CaseModel


class EnvAgent(BaseAgent):
    def __init__(self,
                 model_name='gpt-4o-mini',
                 max_memory_records=10,
                 ):
        super().__init__(
            model_name=model_name,
            max_memory_records=max_memory_records
        )

        self.environment_memory = []
        self.case = None

    def get_current_environment_status(self):
        return self.environment_memory[-1]


    def initialize_environment(
            self,
            case_model: CaseModel
    ):
        # set case
        self.case = case_model

        # generate initialize environment data using case and environment model
        response_init = self.client.beta.chat.completions.parse(
            messages=[
                {
                    "role": "user",
                    "content": f"Initialize the environment data model with case description for biology invasion experiment."
                               f"The environment initialization will be the time when invasion happens and if no external factors, the invasion will expand."
                               f"Use a environment that fits for invasion specie {case_model.invasive_specie_name}  but not for native specie {case_model.native_specie_name}."
                }
            ],
            model=self.model_name,
            response_format=EnvironmentModel
        )

        # change to json using pydantic
        output_init = response_init.choices[0].message.parsed
        output_json = output_init.model_dump()

        # store environment data
        self.environment_memory.append(output_json)

        return output_init

    async def predict_environment(
            self,
            agent_status_list: list[dict],
            env_change_condition: str,
            user_instruction: str = None
    ):
        # last self.max_memory_records records
        if user_instruction:
            user_prompt = """
            Environment history data in the past month:
            {{environment_memory}}
            
            The current bio status:
            {{agent_status_list}}
            
            The environment original changing regular pattern:
            {{env_change_condition}}
            
            External factors:
            {{user_instruction}}
            """
            user_prompt = user_prompt.replace(
                '{{user_instruction}}', user_instruction,
            ).replace(
                '{{agent_status_list}}', str(agent_status_list),
            ).replace(
                '{{env_change_condition}}', env_change_condition,
            ).replace(
                '{{environment_memory}}', str(self.environment_memory[-self.max_memory_records:]),
            )

        else:
            user_prompt = """
                        Environment history data in the past month:
                        {{environment_memory}}

                        The current bio status:
                        {{agent_status_list}}

                        The environment original changing regular pattern:
                        {{env_change_condition}}
                        """

            user_prompt = user_prompt.replace(
                '{{agent_status_list}}', str(agent_status_list),
            ).replace(
                '{{env_change_condition}}', env_change_condition,
            ).replace(
                '{{environment_memory}}', str(self.environment_memory[-self.max_memory_records:]),
            )

        # generate predict environment data using case and environment model
        response_predict = await self.async_client.beta.chat.completions.parse(
            messages=[
                {
                    "role": "system",
                    "content": "Predict the environment data model in the next month with the current environment data, the bio status, "
                               "environment original changing regular pattern."
                               "Keep irrelevant factors unchanged."
                },
                {
                    "role": "user",
                    "content": env_change_condition
                },
            ],
            model=self.model_name,
            response_format=EnvironmentModel
        )

        # change to json using pydantic
        output_predict = response_predict.choices[0].message.parsed
        output_json = output_predict.model_dump()

        # store environment data
        self.environment_memory.append(output_json)

        return output_predict

if __name__ == '__main__':
    env_agent = EnvAgent()
    import os
    import asyncio
    from simulator.utils import get_project_root

    case_path = os.path.join(
        get_project_root(), 'data/cases.json'
    )

    import json

    with open(case_path, 'r', encoding='utf-8') as f:
        cases = json.load(f)

    cases = cases['cases_list']
    import random

    random_case = cases[random.randint(0, len(cases) - 1)]

    output = env_agent.initialize_environment(
        case_model=CaseModel(**random_case)
    )

    print(f'output: {output}')

    # print the next month environment prediction async
    loop = asyncio.get_event_loop()

    output = loop.run_until_complete(
        env_agent.predict_environment(
            agent_status_list=[{
                "bio_name": "fish",
                "bio_num": 100,
                "bio_density": 10,
            }],
            env_change_condition="The weather will be sunny and rainy.",
        )
    )




    print(f'output: {output}')
