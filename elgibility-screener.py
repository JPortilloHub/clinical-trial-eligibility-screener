#!git clone https://github.com/JPortilloHub/clinical-trial-eligibility-screener.git
#import anthropic
from pypdf import PdfReader

#1. Read clinical protocol and save it in a string
file_path = "clinical-trial-protocol.pdf"
clinical_trial_protocol = PdfReader(file_path)

#2. and extract the part you are interested in: Eligibility criteria
extraction_prompt: f"""" You are a a clinician, and your task is to extract the section Patient Selection Criteria, 
including Inclusion Criteria and Exclusion Criteria from the document in pdf wihtin curly brackets. 
Return only the text of that section

<document>
{clinical_trial_protocol}
</document>
"""