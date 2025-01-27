from typing import Optional
from openai import AsyncOpenAI
from pydantic import BaseModel, Field
from simulator.types import CaseModel
from pypdf import PdfReader

class PDFValidationResult(BaseModel):
    is_valid: bool = Field(
        description="Whether the PDF is a valid biology invasion paper"
    )
    reason: str = Field(
        description="Reason why the PDF is valid or invalid"
    )

async def validate_pdf_content(pdf_text: str) -> PDFValidationResult:
    """
    First step: Validate if the PDF is a biology invasion paper
    """
    client = AsyncOpenAI()
    
    prompt = f"""
    Analyze the following text from a PDF and determine if it's a scientific paper about biological invasion.
    Focus on identifying:
    1. If it discusses invasive species and their impact on native species
    2. If it contains scientific observations or experimental data
    3. If it's from a scientific/academic source

    Text:
    {pdf_text}...

    Provide your analysis in a structured format.
    """

    response = await client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        response_format=PDFValidationResult,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    result = PDFValidationResult.model_validate_json(response.choices[0].message.content)
    return result

async def extract_case_data(pdf_text: str) -> CaseModel:
    """
    Second step: Extract relevant fields to create a case model
    """
    client = AsyncOpenAI()
    
    prompt = f"""
    Extract information from the following biology invasion paper to create a structured case.

    Text:
    {pdf_text}...

    Format the response to match these fields exactly:
    - scenario
    - invasive_specie_name
    - invasive_specie_initial_number
    - invasive_specie_initial_density
    - native_specie_name
    - native_specie_initial_number
    - native_specie_initial_density
    - summary
    - mitigation_measures
    - experiment_condition
    - evaluation_criteria
    - weather_changing_description
    """

    response = await client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        response_format=CaseModel,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    case_data = CaseModel.model_validate_json(response.choices[0].message.content)
    return case_data

async def process_pdf_file(
        file_path: str,
        max_characters: int = 5000
        ) -> tuple[bool, str, Optional[CaseModel]]:
    """
    Main pipeline function to process PDF files

    We keep the text length to 5000 characters to avoid the cost of the API call.
    """
    try:
        # Extract text from PDF
        reader = PdfReader(file_path)
        pdf_text = ""
        for page in reader.pages:
            pdf_text += page.extract_text()
            
        if not pdf_text.strip():
            return False, "Could not extract text from PDF", None
        
        # Step 1: Validate the PDF
        validation_result = await validate_pdf_content(pdf_text)
        
        if not validation_result.is_valid:
            return False, validation_result.reason, None
        
        
        # keep the text length to 5000 characters to avoid the exceed of context length.
        pdf_text = pdf_text[:max_characters]
        
        # Step 2: Extract case data
        case_data = await extract_case_data(pdf_text)
        
        return True, "Successfully processed PDF", case_data
        
    except Exception as e:
        return False, f"Error processing PDF: {str(e)}", None 