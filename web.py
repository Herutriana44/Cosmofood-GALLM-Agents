import streamlit as st
import agents

def run_agents(calories, body_weight, sugar, population_size, n_ingredients, gemini_api_key=""):
  """Runs the CosmoFood agents and returns the result.

  Args:
      calories (int): Target calorie intake.
      body_weight (int): User's body weight.
      sugar (int): Target sugar intake.
      population_size (int): Population size for the genetic algorithm.
      n_ingredients (int): Number of ingredients for the recipe recommendation.
      gemini_api_key (str, optional): Optional Gemini API key for additional data. Defaults to "".

  Returns:
      dict: Dictionary containing a success message and the recommendation result.
  """
  try:
      SF_Agents = agents.CosmoFood(calories, body_weight, sugar, population_size, n_ingredients, gemini_api_key)
      Agents_res = SF_Agents.run()
      return {
          "message": "Recommendation Successful",
          "result": Agents_res
      }
  except Exception as e:
      return {
          "message": f"Error: {e}"
      }

# Streamlit app layout
st.title("CosmoFood - GALLM")

# Input fields
calories = st.number_input("Target Calories", min_value=100, max_value=5000, value=2500)
body_weight = st.number_input("Body Weight (kg)", min_value=30, max_value=200, value=80)
sugar = st.number_input("Target Sugar Intake (g)", min_value=0, max_value=500, value=100)
population_size = st.number_input("Population Size (for optimization)", min_value=10, max_value=1000, value=100)
n_ingredients = st.number_input("Number of Ingredients", min_value=2, max_value=10, value=3)
gemini_api_key = st.text_input("Gemini API Key (Optional)", value="")

# Run button
run_button = st.button("Get Recommendations")

if run_button:
  # Run agents and display results
  result = run_agents(calories, body_weight, sugar, population_size, n_ingredients, gemini_api_key)
  st.write(result["message"])
  if "result" in result:
    st.json(result["result"])