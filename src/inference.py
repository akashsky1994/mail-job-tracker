import os
from transformers import AutoTokenizer, AutoModelForCausalLM
import transformers
import torch
import openai
from ratelimit import limits, RateLimitException, sleep_and_retry
from config import MAX_CALLS_PER_MINUTE,ONE_MINUTE
from tenacity import retry,wait_exponential,wait_random_exponential


openai.api_key = os.environ['OPENAI_API_KEY']

class LLMInference():
    def __init__(self) -> None:
        pass
    
    def infer(self):
        raise NotImplementedError
    
    # def check_resp(self):



class GPTInference(LLMInference):
    def __init__(self, model="gpt-3.5-turbo",temperature=0) -> None:
        super().__init__()
        self.model = model
        self.temperature = temperature

    @retry(wait=wait_exponential(multiplier=1, min=4, max=10))
    def infer(self,prompt):
        messages = [{"role": "user", "content": prompt}]
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature, # this is the degree of randomness of the model's output
            )
            return response.choices[0].message["content"] 
        except openai.error.OpenAIError as e:
            print("Some error happened here.",e)
            raise e
        
    

class FalconInference(LLMInference):
    def __init__(self,model="tiiuae/falcon-7b-instruct") -> None:
        super().__init__()
        self.model = model
        self.tokenizer = AutoTokenizer.from_pretrained(model)
        self.pipeline = transformers.pipeline(
            "text-generation",
            model=self.model,
            tokenizer=self.tokenizer,
            torch_dtype=torch.bfloat16,
            trust_remote_code=True,
            device_map="auto",
        )
    
    def infer(self,prompt):
        sequences = self.pipeline(
            prompt,
            max_length=200,
            do_sample=True,
            top_k=10,
            num_return_sequences=1,
            eos_token_id=self.tokenizer.eos_token_id,
        )
        return sequences
        # for seq in sequences:
        #     print(f"Result: {seq['generated_text']}")



def infer_mail(mail_content,type="falcon"):
    if type=="falcon":
        inferenceCls = FalconInference()
    elif type=="openai-gpt":
        inferenceCls = GPTInference()
    else:
        raise NotImplementedError
    prompt = generate_prompt(mail_content)
    return inferenceCls.infer(prompt)
    
def generate_prompt(mail_content):
    prompt = f"""
    Identify the following items from the mail content: 
    - Identify Whether this mail is related to job application. Answer this in boolean (True or False). Differentiate between job listing and job application.
    - Job Position
    - Company to which applied
    - Status of the job application
    - Date present in the mail body
    - Location of the job

    The mail content is delimited with triple backticks. \
    Format your response as a JSON object with \
    "is_job_application", "status", "position", "location", "company_name" and "date" as the keys.
    If the information isn't present, use "null" \
    as the value.
    key "is_job_application" is mandatory field
    Make your response as short as possible.

    mail content: '''{str(mail_content)}'''
    """

    # Format the status value as Applied or Rejected.
    return prompt