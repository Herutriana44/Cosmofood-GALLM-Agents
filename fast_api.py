import agents

# FastAPI library
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pyngrok import ngrok
import nest_asyncio
import uvicorn
import os
import shutil
from typing import List, Union

ngrok.set_auth_token("1TfbVOS48SeXdQ7rJ2do5JjJFxG_4d5K3jMerctfbUsXvidrT")

app = FastAPI()

@app.get('/')
async def root():
  return {'result': 'welcome to CosmoFood - GALLM API'}

@app.post("/agents")
async def Agents(calories : int = 2500, body_weight : int = 80, sugar : int = 100, population_size : int = 100, n_ingredients : int = 3, gemini_api_key : str = ""):
    try:
        SF_Agents = agents.CosmoFood(calories, body_weight, sugar, population_size, n_ingredients, gemini_api_keya)
        Agents_res = SF_Agents.run()
        return {
          "message" : "Recommendation Successfull",
          "result" :  Agents_res
        }
        
    except Exception as e:
    	return {
       "message" : f"Error : {e}"
    }
    
    
listener = ngrok.connect(8000)
# listener = ngrok.forward(8000, authtoken_from_env=True)
print('Public URL:', listener.public_url)
nest_asyncio.apply()
uvicorn.run(app, port=8000)