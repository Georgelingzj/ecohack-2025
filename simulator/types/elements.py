from pydantic import BaseModel


class EnergyFlowModel(BaseModel):
    description: str


class NutrientCyclesModel(BaseModel):
    description: str


class TrophicInteractionsModel(BaseModel):
    description: str


class SuccessionModel(BaseModel):
    description: str


class CarryingCapacityModel(BaseModel):
    description: str


EnergyFlowModel.model_rebuild()
NutrientCyclesModel.model_rebuild()
TrophicInteractionsModel.model_rebuild()
SuccessionModel.model_rebuild()
CarryingCapacityModel.model_rebuild()


class DeforestationModel(BaseModel):
    description: str


class PollutionModel(BaseModel):
    description: str


class ClimateChangeModel(BaseModel):
    description: str


class ResourceExploitationModel(BaseModel):
    description: str


DeforestationModel.model_rebuild()
PollutionModel.model_rebuild()
ClimateChangeModel.model_rebuild()
ResourceExploitationModel.model_rebuild()


class ClimateModel(BaseModel):
    temperature: float
    precipitation: float
    humidity: float
    wind: float


class SoilChemistryModel(BaseModel):
    pH: float
    salinity: float
    nitrogen: float
    phosphorus: float


class SunlightModel(BaseModel):
    availability: float
    intensity: float
    duration: float
    quality: float


ClimateModel.model_rebuild()
SoilChemistryModel.model_rebuild()
SunlightModel.model_rebuild()


class AbioticModel(BaseModel):
    climate: ClimateModel
    soil_chemistry: SoilChemistryModel
    sunlight: SunlightModel


class HumanFactorModel(BaseModel):
    deforestation: DeforestationModel
    pollution: PollutionModel
    climate_change: ClimateChangeModel
    resource_exploitation: ResourceExploitationModel


class EcologicalProcessModel(BaseModel):
    energy_flow: EnergyFlowModel
    nutrient_cycles: NutrientCyclesModel
    trophic_interactions: TrophicInteractionsModel
    succession: SuccessionModel
    carrying_capacity: CarryingCapacityModel


AbioticModel.model_rebuild()
HumanFactorModel.model_rebuild()
EcologicalProcessModel.model_rebuild()


class EnvironmentModel(BaseModel):
    abiotic: AbioticModel
    human_factor: HumanFactorModel
    #ecological_process: EcologicalProcessModel

