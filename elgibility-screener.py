#!git clone https://github.com/JPortilloHub/clinical-trial-eligibility-screener.git
import anthropic
from pypdf import PdfReader
from langchain_voyageai import VoyageAIEmbeddings
from langchain_chroma import Chroma
import os

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

#1. Read clinical protocol and save it in a string
file_path = "clinical-trial-protocol.pdf"
reader = PdfReader(file_path)
clinical_trial_protocol = ""
for page in reader.pages:
    clinical_trial_protocol += page.extract_text()

#2. and extract the part you are interested in: Eligibility criteria
extraction_prompt= f"""" You are a a clinician, and your task is to extract the section Patient Selection Criteria, 
including Inclusion Criteria and Exclusion Criteria from the document in pdf wihtin curly brackets. 
Return only the text of that section

<document>
{clinical_trial_protocol}
</document>
"""

response = client.messages.create(
    model = "claude-haiku-4-5-20251001",
    max_tokens = 2000,
    messages = [{"role": "user", "content": extraction_prompt}]
)

eligibility_criteria_extraction = response.content[0].text


#3 Embed the eligibility criteria into the vector database
eligibility_criteria_embedded = VoyageAIEmbeddings(model= "voyage-3", voya_api_key= os.environ.get("VOYAGE_API_KEY"))

eligibility_criteria_vector_db = Chroma.from_texts(
    texts=[eligibility_criteria_extraction],
    embedding=eligibility_criteria_embedded,
    collection_name="eligibility_criteria",
    metadatas=[{"source": "clinical-trial-protocol.pdf", "section": "Patient Selection Criteria"}]
)

