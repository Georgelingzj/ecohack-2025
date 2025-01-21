from camel.agents import ChatAgent
from camel.configs import DeepSeekConfig
from camel.messages import BaseMessage
from camel.models import ModelFactory
from camel.tasks import Task
from camel.toolkits import FunctionTool, SearchToolkit
from camel.types import ModelPlatformType, ModelType
from camel.societies.workforce import Workforce
from camel.agents import ChatAgent
from camel.messages import BaseMessage
from camel.schemas import OutlinesConverter

from camel.types import (
    RoleType,
)

from simulator.types import (
    Model4Use, EnvironmentModel
)

import os
from dotenv import load_dotenv

load_dotenv()

outliner_model = OutlinesConverter(
    model_type="/Users/lingzijian/projects/ecohack-Jan20-2025/Qwen2.5-0.5B-Instruct"
)
print(f'outliner_model: {outliner_model}')

MODEL_TO_USE = Model4Use.get_key(os.getenv("model_4_use"))
if MODEL_TO_USE == Model4Use.DEEPSEEK:
    api_key = os.environ["DEEPSEEK_API_KEY"]
    api_url = os.environ["DEEPSEEK_API_URL"]
    model_name = "deepseek-chat"
elif MODEL_TO_USE == Model4Use.GPT_4o_MINI:
    api_key = os.environ["OPENAI_API_KEY"]
    api_url = os.environ["OPENAI_API_URL"]
    model_name = "gpt-4o-mini"
else:
    raise ValueError(f"Unknown model to use: {MODEL_TO_USE}")

env_model = ModelFactory.create(
    model_platform=ModelPlatformType.OPENAI_COMPATIBLE_MODEL,
    model_type=model_name,
    api_key=api_key,
    url=api_url,
    model_config_dict=DeepSeekConfig(temperature=1.0).as_dict(),
)

system_prompt_init = '''
You are a environment agent. You are responsible for creating a natural environment as real as possible based on given condition.
'''

system_prompt_during_game = """
You are a environment agent. You are responsible for transforming the input description to a natural environment change.

You should first understand the relation of input description and its relevant elements in the natural environment, 
You should keep irrelevant elements unchanged.

Then return the new environment as the following schema:
{{schema}}
"""

system_prompt_during_game.replace('{{schema}}', EnvironmentModel.schema_json(indent=4))

env_agent = ChatAgent(
    system_message=system_prompt_init,
    model=env_model,
    output_language='English'
)


def initialize_environment(
        user_input_condition: str,
):
    """
    Initialize the environment based on the given condition.

    :param user_input_condition: The input condition to initialize the environment.
    :return: The initialized environment.
    """
    output = env_agent.step(user_input_condition, response_format=EnvironmentModel)

    # change system prompt
    env_agent.system_message = system_prompt_during_game


    return output



def environment_step(
        user_input_description: str,
        current_environment: EnvironmentModel
):
    """
    Transform the input description to a natural environment change.

    :param user_input_description: The input description to transform.
    :param current_environment: The current environment.
    :return: The new environment.
    """
    output_raw = env_agent.step(user_input_description)
    output = outliner_model.convert_pydantic(output_raw.msgs[0].content, EnvironmentModel)
    return output


if __name__ == '__main__':
    print(f'running workforce with model: {model_name}')

    print(env_agent.step(
        'The Great Lakes suffer as invasive zebra mussels rapidly multiply, outcompeting native species for food, '
        'clogging water intake systems, and disrupting the aquatic ecosystem.',
        response_format=EnvironmentModel
    )
    )

    curr_history = env_agent.memory.get_context()
    print(f'Current history: {curr_history}')

    # change system prompt
    env_agent.system_message = system_prompt_during_game

    next_env = env_agent.step(
        "Higher temperatures.",
    )

    next_env = outliner_model.convert_pydantic(next_env.msgs[0].content, EnvironmentModel)
    print(f'Next environment: {next_env}')
    curr_history = env_agent.memory.get_context()
    print(f'Current history: {curr_history}')
