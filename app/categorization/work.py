from datetime import datetime
import json
from typing import Dict, Any, Union
from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import PromptTemplate
from langchain.chains import SequentialChain

from llm_helper import (
    is_years,
    is_bounded,
    is_european_decimal,
    is_float,
    is_integer,
    is_iso8601,
   
    SexLevel,
    AgeFormat

)
from promptTemplate import(
    Aprompt,
    Dprompt
)
pass2={}
pass3={}



def llm_invocation(result_dict: Dict[str, str]) -> Dict[str, Any]:

    # Initialize model
    llm = ChatOllama(model="gemma")

    # Create prompt template
    prompt = PromptTemplate(
        template="""Given the column data {column}: {content}, determine the category and give only the category name as output based on the examples and description for each category.
Instruction consider these examples to decide what {column}: {content} fits in what category.

1. Input: "participant_id: sub-01 sub-02 sub-03"
description : giving serial no. to each participant.
Output: Participant_IDs

2. Input: 'contains words from {age} or conveying the same meaning ': [34 45 56 56.7 45,5 66.8 3 2 4 ]'
description: Indicates the age that is how old is an individual.
Output: Age

3. Input: "session_id" or "session": "ses-01 ses-02" or "1 2 1 1 2..."
Descriptions : shows the session no. and do not include data with the word "group"
Output: Session_IDs

4. Input: "pheno_sex" or "Sex" : ["F", "F", "M", "M", "missing",
"missing", "F", "F", "M", "M"] or ["1", "2", "1", "2", "missing", "missing"]"
Description: represents the Sex that is the gender using M F or 0 1 2
Output: Sex





Do Not Give any explanation in the output.
Input: "{column}: {content}"
Output= <category>
""",
        input_variables=["column", "content","age"],
    )
    
    # Create chain
    chain = prompt |llm
    
    # chain = SequentialChain(
#     chains=[chain1,chain2],
#     input_variables=["column","content"]
# )
    

    

    age = { "pheno_age","age","Age"}
    #key, value = list(result_dict.items())[0]
    for key, value in result_dict.items():

    # Invoke LLM
        llm_response = chain.invoke({"column": key, "content": value,"age":age})

        r = str(llm_response)
    # check mapping of categorization
        #print(llm_response)
        if "Participant_IDs" in r:
            output = {"TermURL": "nb:ParticipantID"}
            print(f"{json.dumps(output)}")
        elif "Session_IDs" in r or "session" in r.lower():
            output = {"TermURL": "nb:Session"}
            print(f"{json.dumps(output)}")
        elif "sex" in r.lower():
            output = SexLevel(result_dict, r, key)
            print(f"{json.dumps(output)}")
        elif "Age" in r:
            output = AgeFormat(result_dict, r, key)
            print(f"{json.dumps(output)}")
        # elif "Diagnosis" in r:
        #   print("Processing column:", key)
        #   output = {"TermURL": "nb:diagnosis"}
        #   print(f"{json.dumps(output)}")
        else:
            pass2[key]=value


    print(pass2.keys())
    return output

def D():
    for key, value in pass2.items():
        print(key)
        llm = ChatOllama(model="gemma")
        
        chainD =Dprompt | llm
        
        llm_response2 = chainD.invoke({"column": key, "content": value})
        reply = str(llm_response2)
        # print(reply)
        if "yes" in reply.lower():
            # print("Processing column:", key)
            output = {"TermURL": "nb:D"}
            print(f"{json.dumps(output)}")
        else:
            pass3[key]=value
    print(pass3.keys())

def A():
    for key, value in pass3.items():
        print(key)
        llm = ChatOllama(model="gemma")
        questionA=f"Is the {key}:{value} a assesment tool"
        # chainD =Dprompt | llm
        chainA =Aprompt | llm
        llm_response2 = chainA.invoke({"column": key, "content": value,"question":questionA})
        reply = str(llm_response2)
        # print(reply)
        if "yes" in reply.lower():
            # print("Processing column:", key)
            output = {"TermURL": "nb:A"}
            print(f"{json.dumps(output)}")
        else:
            print("not in data model")

        
        
    
    

if __name__ == "__main__":
  result_dict = {'participant_id': 'participant_id sub-718211 sub-718213 sub-718216 sub-718217 sub-718220 sub-718221 sub-718315 sub-718318 sub-718320 sub-718321 sub-718322 sub-718323 sub-718518 sub-719211 sub-719215 sub-719222 sub-719224 sub-719225 sub-719226 sub-719231 sub-719232 sub-719238 sub-719241 sub-719245 sub-719247 sub-719311 sub-719312 sub-719313 sub-719315 sub-719316 sub-719318 sub-719319 sub-719322 sub-719326 sub-719327 sub-719329 sub-719330 sub-719331 sub-719332 sub-719334 sub-719335 sub-719337 sub-719339 sub-719341 sub-719345 sub-719348 sub-719349 sub-719350 sub-719351 sub-719354 sub-719355 sub-719356 sub-719358 sub-719360 sub-719362 sub-719364 sub-719369 sub-719370 sub-719371 sub-719511 sub-719515 sub-719518 sub-719522 sub-719523 sub-719524 sub-719525 sub-719526 sub-719527 sub-719528 sub-719530 sub-719531 sub-719535 sub-719536 sub-720219 sub-720220 sub-720311 sub-720312 sub-720314 sub-720316 sub-720317 sub-720318 sub-720319 sub-720320 sub-720511 sub-720515 sub-720516 sub-720517', 'age': '026Y 024Y 046Y 026Y 026Y 023Y 029Y 030Y 019Y 023Y 023Y 027Y 031Y 026Y 025Y 024Y 028Y 032Y 033Y 023Y 023Y 025Y 030Y 026Y 022Y 027Y 021Y 024Y 038Y 026Y 024Y 046Y 026Y 026Y 023Y 029Y 030Y 019Y 023Y 023Y 027Y 031Y 026Y 025Y 024Y 028Y 032Y 033Y 023Y 023Y 025Y 030Y 026Y 022Y 027Y 021Y 024Y 038Y 026Y 024Y 046Y 026Y 026Y 023Y 029Y 030Y 019Y 023Y 023Y 027Y 031Y 026Y 025Y 024Y 028Y 032Y 033Y 023Y 023Y 025Y 030Y 026Y 022Y 027Y 021Y 024Y 038Y', 'sex': 'sex 1 2 1 2 2 2 2 2 1 2 2 2 2 1 2 2 2 2 2 2 2 2 2 1 2 1 2 1 2 2 2 1 1 2 2 2 2 2 1 2 2 2 2 2 2 2 1 2 1 2 1 2 2 2 1 2 2 2 2 2 2 2 2 2 1 2 2 2 1 2 2 1 1 1 2 2 1 2 1 2 2 2 2 1 2 2 2', 'group': ' AD AD AD AD AD AD HC HC HC HC MCI HC AD AD AD AD AD AD AD AD AD AD AD AD AD HC MCI MCI HC HC HC HC HC HC HC HC HC HC HC HC HC HC HC MCI HC HC HC HC MCI HC HC HC HC HC HC HC HC HC HC AD AD AD AD AD AD AD AD AD AD AD AD AD AD AD AD HC HC HC HC HC HC HC HC AD AD AD AD', 'iq': 'iq 117.66 109.08 112.98 114.54 107.52 99.72 104.4 98.16 111.42 108.3 109.86 111.42 108.3 105.96 121.56 110.64 113.76 111.42 114.54 119.22 109.86 109.08 121.56 117.66 110.64 104.4 100.5 111.42 107.52 111.42 109.08 107.52 108.3 113.76 112.98 93.48 101.28 96.6 115.32 103.62 102.84 95.82 105.18 102.06 98.16 102.06 105.96 91.92 114.54 105.96 109.86 103.62 107.52 102.84 105.96 111.42 108.3 108.3 113.76 109.08 120.78 118.44 119.22 100.5 108.3 115.32 102.84 116.88 109.86 118.44 102.06 107.52 88.8 110.64 99.72 114.54 122.34 112.98 106.74 102.06 110.64 105.96 115.32 102.84 109.86 105.18 95.82', 'stroop': 'stroop 326 528 240 502 271 417 335 493 292 257 469 567 472 381 383 224 455 204 368 448 359 579 330 485 389 245 300 278 469 377 421 249 563 270 447 422 552 259 246 356 415 382 437 425 252 202 462 405 510 552 577 393 560 442 353 324 395 489 210 267 523 514 524 301 551 590 409 452 405 598 442 222 228 573 234 482 517 543 383 411 388 303 569 423 461 538 202'}


  llm_invocation(result_dict)
  D()
  A()