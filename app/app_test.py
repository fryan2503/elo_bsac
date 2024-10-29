import json
import random
from datetime import datetime

import numpy as np
import pandas as pd
from flask import Flask, redirect, render_template, request, url_for
from pymongo import MongoClient

app = Flask(__name__)



client = MongoClient('mongodb://singhr7:farmerbigdata@mongodb.fsb.miamioh.edu:27017/', authSource="admin")

'''
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

db = client.singhr7.elo_outcomes_raw
'''

# Load organizations data
organizations = pd.read_csv("clubs.csv")
organizations["Rating"] = 1500  # initial rating

def elo_rating(rating1, rating2, outcome, k=32):

    """
    Calculate the new Elo ratings for two organizations after a match.

    Parameters:
    rating1 (float): The current rating of the first organization.
    rating2 (float): The current rating of the second organization.
    outcome (int): The outcome of the match (1 if org1 wins, 0 if org2 wins, 2 if no match).
    k (int): The K-factor which determines the maximum possible adjustment per match (default is 32).

    Returns:
    tuple: The new ratings for the first and second organizations.
    """
    if outcome == 2:
        # No match took place, return the original ratings
        return rating1, rating2

    # Calculate the expected outcome for org1
    expected1 = 1 / (1 + 10 ** ((rating2 - rating1) / 400))

    # Update the ratings based on the actual outcome
    new_rating1 = rating1 + k * (outcome - expected1)
    new_rating2 = rating2 + k * ((1 - outcome) - (1 - expected1))

    return new_rating1, new_rating2

def select_organizations(organizations_df, clubs_inv, high_rank_prob=0.7, high_rank_threshold=20):
    """
    Selects two organizations from a DataFrame of organizations, ensuring that neither organization is in the 
    provided list of clubs to be excluded. The selection process can favor organizations within a certain rank 
    threshold of each other based on a probability.

    Parameters:
    organizations_df (pd.DataFrame): DataFrame containing organization data. Must have a column named 'Organization'.
    clubs_inv (list): List of organizations to be excluded from selection.
    high_rank_prob (float, optional): Probability of selecting the second organization within a certain rank 
                                      threshold of the first. Default is 0.7.
    high_rank_threshold (int, optional): The rank threshold within which the second organization is selected if 
                                         high_rank_prob condition is met. Default is 20.

    Returns:
    tuple: A tuple containing the names of the two selected organizations.
    """
    num_orgs = len(organizations_df)
    org1_index = random.randint(0, num_orgs - 1)
    org1 = organizations_df.iloc[org1_index]['Organization']

    if org1 in clubs_inv:
        return select_organizations(organizations_df, clubs_inv)

    if random.random() < high_rank_prob:
        start_index = max(0, org1_index - high_rank_threshold)
        end_index = min(num_orgs, org1_index + high_rank_threshold + 1)
        possible_indices = [i for i in range(start_index, end_index) if i != org1_index]
    else:
        possible_indices = [i for i in range(num_orgs) if i != org1_index]

    org2_index = random.choice(possible_indices)
    org2 = organizations_df.iloc[org2_index]['Organization']

    if org2 in clubs_inv:
        return select_organizations(organizations_df, clubs_inv)

    return org1, org2


@app.route('/', methods=['GET', 'POST'])
def index():
    global num_comparison
    if request.method == 'POST':
        name = request.form.get('name', 'Anonymous')
        num_comparison = int(request.form.get('num_comparisons'))
        clubs_inv = request.form.getlist('clubs_inv')
        return redirect(url_for('survey', name=name, num_comparisons=num_comparison, clubs_inv=json.dumps(clubs_inv)))
    return render_template('index.html', organizations=organizations['Organization'].tolist())


@app.route('/survey/', methods=['GET', 'POST'])
def survey(organizations = organizations):
    name = request.args.get('name', 'Anonymous')
    clubs_inv = request.args.get('clubs_inv', '[]')

    if request.method == 'POST':
        comparisons = []

        for i in range(num_comparison):
            org1 = request.form.get(f'org1_{i}')
            org2 = request.form.get(f'org2_{i}')
            outcome = int(request.form.get(f'outcome_{i}'))
            comparisons.append({'Org1': org1, 'Org2': org2, 'Outcome': outcome})

            # Update ratings
            rating1 = organizations.loc[organizations['Organization'] == org1, 'Rating'].values[0]
            rating2 = organizations.loc[organizations['Organization'] == org2, 'Rating'].values[0]
            new_rating1, new_rating2 = elo_rating(rating1, rating2, outcome)
            organizations.loc[organizations['Organization'] == org1, 'Rating'] = new_rating1
            organizations.loc[organizations['Organization'] == org2, 'Rating'] = new_rating2
            organizations = organizations.reset_index(drop=True).sort_values(by='Rating', ascending=False)


        # Prepare data for MongoDB
        to_mongo = {
            "name": name,
            "clubs_involved": clubs_inv,
            **{f"round:{i}": comparisons[i] for i in range(len(comparisons))},
            "Date": datetime.now()
        }

        # Insert into MongoDB
        # db.insert_one(to_mongo)
        print(organizations.head())
        return render_template('thank_you.html', name=name)

    # If it's a GET request, prepare the survey
    org1s = []
    org2s = []
    for _ in range(num_comparison):
        org1, org2 = select_organizations(organizations, clubs_inv)
        org1s.append(org1)
        org2s.append(org2)
    
    return render_template('survey.html', name=name, num_comparisons=num_comparison, org1s=org1s, org2s=org2s)
    

if __name__ == '__main__':
    app.run(debug=True)