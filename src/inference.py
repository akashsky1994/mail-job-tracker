import os
from transformers import AutoTokenizer, AutoModelForCausalLM
import transformers
import torch
import openai
openai.api_key = os.environ['OPENAI_API_KEY']

class LLMInference():
    def __init__(self) -> None:
        pass
    
    def infer(self):
        raise NotImplementedError


class GPTInference(LLMInference):
    def __init__(self, model="gpt-3.5-turbo",temperature=0) -> None:
        super().__init__()
        self.model = model
        self.temperature = temperature

    def infer(self,prompt):
        messages = [{"role": "user", "content": prompt}]
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature, # this is the degree of randomness of the model's output
        )
        return response.choices[0].message["content"] 
    

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
    return inferenceCls(prompt)
    
def generate_prompt():
    pass