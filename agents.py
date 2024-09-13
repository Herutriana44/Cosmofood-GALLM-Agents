import requests
import os
import pandas as pd
import random

n_ingredients, TARGET, GENES = None, None, None

nutrient_df = pd.read_excel("clean_nutrient.xlsx")
df = pd.read_excel("clean_ingredients_float.xlsx")

all_id_ingredients = df["NDB_No"].tolist()
all_name_ingredients = df["Descrip"].tolist()


def calculate_total_nutrient_by_ingredients(ingredients):
  total_nutrient = {}
  for i in range(len(ingredients)):
    ingredient = get_nutrient_by_id(ingredients[i])

    # convert all ingredients nutrients to float
    for x, y in ingredient.items():
      ingredient[x] = float(ingredient[x])

    for x, y in ingredient.items():
      if x in total_nutrient.keys():
        total_nutrient[x] += ingredient[x]
      else:
        total_nutrient[x] = ingredient[x]

  return total_nutrient
  
def fitting_function(ingredients, person_nutrient_dict):
  total_nutrient = {}
  total_nutrient_of_ingredients = calculate_total_nutrient_by_ingredients(ingredients)
  for x, y in person_nutrient_dict.items():
    total_nutrient[x] = person_nutrient_dict[x] - total_nutrient_of_ingredients[x]

  return total_nutrient
  
def get_nutrient_by_id(id):
  res_series = df[df["NDB_No"] == id]
  res_value = {}
  for i in range(2, len(res_series.columns)):
    res_value[res_series.columns[i]] = res_series.iloc[0][i]
  return res_value

def ingredient_id_to_name(id):
  ingredient_dict = {key : value for key, value in zip(df["NDB_No"], df["Descrip"])}
  return ingredient_dict[id]
  
  
def get_all_of_names_ingredients(ingredients):
  all_names = []
  for i in range(len(ingredients)):
    all_names.append(ingredient_id_to_name(ingredients[i]))
  return all_names
  
  
class GeminiAgent():
    def __init__(self, ingredients, api_key=""):
        self.ingredients = ingredients
        self.api_key = api_key
        
    def prompt_templating_process_1(self):
        all_names = get_all_of_names_ingredients(self.ingredients)
        prompt = f"""
    Develop a space food recipe or dry food processing method using various food technology methods with the following ingredients:
    {", ".join(all_names)}
  """.strip()

        return prompt


    def prompt_templating_process_2(prompts):
      prompt = f"""
    Make a financial budget plan such food technology tools, ingredients, and others with the following explain:
    {prompts}
    Create in tabular data likes csv
  """.strip()
  
      return prompt
  
    def gemini(self, prompt):
        url = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={self.api_key}'
        headers = {
            'Content-Type': 'application/json'
        }
        data = {
            "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ]
    }

        response = requests.post(url, headers=headers, json=data)

        if response.status_code == 200:
            result = response.json()
            text_response = result["candidates"][0]["content"]["parts"][0]["text"]
            return text_response, result
        else:
            return f"Request failed with status code {response.status_code}"
        
        
    def run(self):
        ingredients_ = self.prompt_templating_process_1()
        food_design = self.gemini(ingredients_)
        financial_design = self.gemini(food_design)
        
        return {'food_design':food_design, 'financial_design':financial_design}
  
class Individual(object):
  def __init__(self, chromosome):
    self.chromosome = chromosome
    self.fitness = self.cal_fitness()

  @classmethod
  def mutated_genes(self):
    # create random genes for mutation
    global GENES
    gene = random.choice(GENES)
    return gene

  @classmethod
  def create_gnome(self):
    # create chromosome or string of genes
    global TARGET, n_ingredients
    gnome_len = n_ingredients
    return [self.mutated_genes() for _ in range(gnome_len)]

  def mate(self, par2):
    # Perform mating and produce new offspring
    # chromosome for offspring
    child_chromosome = []
    for gp1, gp2 in zip(self.chromosome, par2.chromosome):
      # random probability
      prob = random.random()
      #if prob is less than 0.45, insert gene # from parent 1
      if prob < 0.45:
        child_chromosome.append(gp1)
      # if prob is between 0.45 and 0.90, insert # gene from parent 2
      elif prob < 0.90:
        child_chromosome.append(gp2)
      # otherwise insert random gene (mutate), # for maintaining diversity
      else:
        child_chromosome.append(self.mutated_genes())

    #create new Individual (offspring) using
    #generated chromosome for offspring
    return Individual(child_chromosome)

  def cal_fitness(self):
    """
    Calculate fitness score, it is the number of characters in string which differ from target string.
    """
    global TARGET
    fitness = 0
    fit_calc = fitting_function(self.chromosome, TARGET)
    fit_calc_num = sum([y for x, y in fit_calc.items()])

    return fit_calc_num

class CosmoFood:     
    def __init__(self, kalori, berat, gula, POPULATION_SIZE=100, n_ingredients_=3, gemini_api_key = ""):
        self.kalori = kalori
        self.berat = berat
        self.gula = gula
        self.POPULATION_SIZE = POPULATION_SIZE
        self.n_ingredients = n_ingredients_

        # Load data (asumsikan sudah dalam format yang benar)
        self.nutrient_df = pd.read_excel("clean_nutrient.xlsx")
        self.df = pd.read_excel("clean_ingredients_float.xlsx")
        self.all_id_ingredients = self.df["NDB_No"].tolist()
        self.all_name_ingredients = self.df["Descrip"].tolist()
        self.GENES = self.all_id_ingredients
        
        self.nutrient_dict = {key : value for key, value in zip(self.nutrient_df["Nutrient"], self.nutrient_df["Daily Needs"])}
        
        # nutrient_dict = {key : value for key, value in zip(nutrient_df["Nutrient"], nutrient_df["Daily Needs"])}
        self.target_nutrient_dict = {key : 0.0 for key, value in zip(self.nutrient_df["Nutrient"], self.nutrient_df["Daily Needs"])}
       
        # Hitung target nutrisi
        self.TARGET = self.calculate_nutrient(self.kalori, self.berat, self.gula)
        
        global n_ingredients, TARGET, GENES
        n_ingredients = self.n_ingredients
        TARGET = self.TARGET
        GENES = self.GENES
        
    
    def calculate_nutrient(self, total_calories, weight, sugar):
        nutrient_dict = {key : value for key, value in zip(self.nutrient_df["Nutrient"], self.nutrient_df["Daily Needs"])}
        nutrient_dict["Energy_kcal"] = total_calories
        nutrient_dict["Protein_g"] = 1 * weight
        nutrient_dict["Saturated_fats_g"] = 0.09 * total_calories
        nutrient_dict["Fat_g"] = 0.35 * total_calories
        nutrient_dict["Carb_g"] = 0.65 * total_calories
        nutrient_dict["Sugar_g"] = sugar
        return nutrient_dict
        
    

    # ... (fungsi-fungsi lain yang sudah ada)

    def run(self):
        # Implementasi algoritma genetika (sama seperti sebelumnya)

        # Contoh penggunaan:
        generation = 1
        found = False
        population = []
        for _ in range(self.POPULATION_SIZE):
            gnome = Individual.create_gnome()
            population.append(Individual(gnome))

        # ... (sisanya sama seperti sebelumnya)
        while not found:
            #sort the population in increasing order of fitness score
            population = sorted(population, key = lambda x:x.fitness)
		    #if the individual having Lowest fitness score te.
		    #0 then we know that we have reached to the target and break the Loop
            if population[0].fitness <= 0:
               found = True
               break
		    #Otherwise generate new offsprings for new generation
            new_generation = []
		    # Perform Elitism, that mean 10% of fittest population
		    #goes to the next generation
            s = int((10*self.POPULATION_SIZE)/100)
            new_generation.extend(population[:s])
		    #From 50% of fittest population, Individuals
		    #will mate to produce offspring
            s = int((90*self.POPULATION_SIZE)/100)
            for _ in range(s):
               parent1 = random.choice(population[:50])
               parent2 = random.choice(population [:50])
               child = parent1.mate(parent2)
               new_generation.append(child)
            population = new_generation
            print("Generation: {}\tString: {}\tFitness: {}".format(generation,",".join(population[0].chromosome), population[0].fitness))
            generation += 1
        print("Generation: {}\tString: {}\tFitness: {}".format(generation,",".join(population[0].chromosome), population[0].fitness))
        print("Ingredients: ", get_all_of_names_ingredients(population[0].chromosome))
        llm_res = GeminiAgent(population[0].chromosome,self.gemini_api_key).run()
        return population[0].chromosome, llm_res
        
  

# Contoh penggunaan kelas
# cosmo_food = CosmoFood(2500, 100, 36)
# cosmo_food.run()
