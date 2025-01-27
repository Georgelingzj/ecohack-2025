from simulator.agents import BaseAgent

from simulator.types import BioModel


class BioAgent(BaseAgent):
    def __init__(self,
                 model_name='gpt-4o-mini',
                 max_memory_records=10,
                 ):
        super().__init__(
            model_name=model_name,
            max_memory_records=max_memory_records
        )

        self.life_memory = []
        self.bio_name = None
        self.bio_role = None
        self.bio_num = 0
        self.bio_density = 0


    def get_current_bio_status_list(self):
        return self.life_memory[-self.max_memory_records:]

    def initialize_life(
            self,
            bio_name: str,
            bio_role: str,
            bio_num: int,
            bio_density: int,
    ):
        self.bio_name = bio_name
        self.bio_role = bio_role

        init_bio_model = BioModel(
            specie_num=bio_num,
            specie_density=bio_density
        )

        self.life_memory.append(init_bio_model.model_dump())

    async def predict_life(
            self,
            competitor_name: str,
            competitor_num: int,
            competitor_density: int,
            competitor_status_list: list[dict],
            current_environment: dict,
    ):
        user_prompt = f"""
            The current bio status:
            Bio Role: {self.bio_role}
            Bio Name: {self.bio_name}
            Bio Num: {self.life_memory[-1]['specie_num']}
            Bio Density: {self.life_memory[-1]['specie_density']}
            Previous status: {str(self.life_memory[-self.max_memory_records:])},
            
            Current environment status:
            {current_environment}
            
            Competitor Name: {competitor_name}
            Competitor Num: {competitor_num}
            Competitor Density: {competitor_density}
            Competitor previous status:
            {competitor_status_list}
            
            Environment and competitor will increase/decrease bio num and bio density.
            
            You should consider bio competition, environment change, and **reproduction**
    
            However, the invasive bio will suppress the native bio and even kill large numbers of native bio.
            If the environment is favorable for the invasive bio, the invasive bio will grow rapidly.
            
            Predict the **bio status** in the next month non-linearly.
        """

        response = await self.async_client.beta.chat.completions.parse(
            messages=[
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],
            model=self.model_name,
            response_format=BioModel
        )
        output = response.choices[0].message.parsed
        output_json = output.model_dump()
        print(f'predicting bio status: {output_json} for {self.bio_name}')
        # store life data
        self.life_memory.append(output_json)

        return output