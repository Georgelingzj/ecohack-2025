from enum import Enum
from pydantic import BaseModel, Field
from typing import List, Dict, Optional


class Model4Use(Enum):
    GPT_4o_MINI = "gpt-4o-mini"
    DEEPSEEK = "deepseek"

    # a func given str back to Enum, if not found, return None
    # a function to get key from value
    @classmethod
    def get_key(cls, value):
        for key, member in cls.__members__.items():
            if member.value == value:
                return member
        return None


class CaseModel(BaseModel):
    scenario: str = Field(
        title="Scenario",
        description="The scenario of the case, "
                    "including the all relevant biological species involved, interactions, and environmental factors",
    )

    invasive_specie_name: str = Field(
        title="Invasive Specie Name",
        description="The name of the invasive specie.",
    )

    invasive_specie_initial_number: int = Field(
        title="Invasive Specie Initial Number",
        description="The initial number of the invasive specie.",
    )

    invasive_specie_initial_density: int = Field(
        title="Invasive Specie Initial Density",
        description="The initial density of the invasive specie per unit area.",
    )

    native_specie_name: str = Field(
        title="Native Specie Name",
        description="The name of the native specie.",
    )

    native_specie_initial_number: int = Field(
        title="Native Specie Initial Number",
        description="The initial number of the native specie.",
    )

    native_specie_initial_density: int = Field(
        title="Native Specie Initial Density",
        description="The initial density of the native specie per unit area.",
    )

    summary: str = Field(
        title="Summary",
        description="Summarize the biology invasion case in one sentence.",
    )

    mitigation_measures: str = Field(
        title="Mitigation Measures",
        description="The mitigation measures of the case. How to take the measure to alleviate or mitigate invasion ",
    )

    experiment_condition: str = Field(
        title="Experiment Condition",
        description="The specific experimental setup, conditions.",
    )

    evaluation_criteria: str = Field(
        title="Evaluation Criteria",
        description=" The metrics or criteria used to evaluate results to see whether the measure is effective or not.",
    )

    weather_changing_description: str = Field(
        title="Weather Changing Description",
        description="The description of the weather changing in the location of the case across the whole year.",
    )

    invasive_specie_growth_upper: float = Field(
        title="Invasive Specie Growth Rate Upper Bound (Monthly)",
        description="Upper bound of monthly growth rate for invasive species (%)"
    )
    invasive_specie_growth_lower: float = Field(
        title="Invasive Specie Growth Rate Lower Bound (Monthly)",
        description="Lower bound of monthly growth rate for invasive species (%)"
    )
    native_specie_decline_upper: float = Field(
        title="Native Specie Decline Rate Upper Bound (Monthly)",
        description="Upper bound of monthly decline rate for native species (%)"
    )
    native_specie_decline_lower: float = Field(
        title="Native Specie Decline Rate Lower Bound (Monthly)",
        description="Lower bound of monthly decline rate for native species (%)"
    )


class BioModel(BaseModel):
    specie_num: int = Field(
        title="Specie Number",
        description="The number of species in the environment.",
    )

    specie_density: int = Field(
        title="Specie Density",
        description="The density of species in the environment per unit area.",
    )