import json
import random
from datetime import datetime

import numpy as np
import pandas as pd
import streamlit as st
from pymongo import MongoClient

# Initialize MongoDB client
client = MongoClient('mongodb://singhr7:farmerbigdata@mongodb.fsb.miamioh.edu:27017/', authSource="admin")

db = client.singhr7.elo_outcomes_raw

# Load organizations data
organizations = pd.read_csv('app/clubs.csv')
organizations["Rating"] = 1500


def elo_rating(rating1, rating2, outcome, k=32):
    """Calculate new Elo ratings for a match."""
    if outcome == 2:
        return rating1, rating2
    expected1 = 1 / (1 + 10 ** ((rating2 - rating1) / 400))
    new_rating1 = rating1 + k * (outcome - expected1)
    new_rating2 = rating2 + k * ((1 - outcome) - (1 - expected1))
    return new_rating1, new_rating2


def select_organizations(organizations_df, clubs_inv, high_rank_prob=0.7, high_rank_threshold=20):
    """Select two organizations for comparison."""
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


# Streamlit app
st.title("Student Organization Survey")

if "stage" not in st.session_state:
    st.session_state.stage = "setup"
    st.session_state.name = ""
    st.session_state.num_comparisons = 0
    st.session_state.clubs_inv = []
    st.session_state.org_pairs = []
    st.session_state.comparisons = []

if st.session_state.stage == "setup":
    with st.form("setup_form"):
        name = st.text_input("Enter your name")
        num_comp = st.number_input("Number of comparisons", min_value=1, value=1, step=1)
        clubs_inv = st.multiselect("Clubs you're involved in", organizations['Organization'].tolist())
        submitted = st.form_submit_button("Start Survey")
        if submitted:
            st.session_state.name = name or "Anonymous"
            st.session_state.num_comparisons = int(num_comp)
            st.session_state.clubs_inv = clubs_inv
            st.session_state.org_pairs = [select_organizations(organizations, clubs_inv) for _ in range(int(num_comp))]
            st.session_state.stage = "survey"
            st.experimental_rerun()

if st.session_state.stage == "survey":
    with st.form("survey_form"):
        outcomes = []
        for i in range(st.session_state.num_comparisons):
            org1, org2 = st.session_state.org_pairs[i]
            choice = st.radio(f"Comparison {i+1}: {org1} vs {org2}", [org1, org2, "Neither"], key=f"outcome_{i}")
            outcomes.append(choice)
        submitted = st.form_submit_button("Submit Survey")
        if submitted:
            comparisons = []
            for i, choice in enumerate(outcomes):
                org1, org2 = st.session_state.org_pairs[i]
                if choice == org1:
                    outcome = 1
                elif choice == org2:
                    outcome = 0
                else:
                    outcome = 2
                comparisons.append({'Org1': org1, 'Org2': org2, 'Outcome': outcome})
                rating1 = organizations.loc[organizations['Organization'] == org1, 'Rating'].values[0]
                rating2 = organizations.loc[organizations['Organization'] == org2, 'Rating'].values[0]
                new_rating1, new_rating2 = elo_rating(rating1, rating2, outcome)
                organizations.loc[organizations['Organization'] == org1, 'Rating'] = new_rating1
                organizations.loc[organizations['Organization'] == org2, 'Rating'] = new_rating2
            organizations.sort_values(by='Rating', ascending=False, inplace=True, ignore_index=True)
            to_mongo = {
                "name": st.session_state.name,
                "clubs_involved": st.session_state.clubs_inv,
                "time": datetime.now(),
                **{f"round:{i}": comparisons[i] for i in range(len(comparisons))},
                "Date": datetime.now()
            }
            db.insert_one(to_mongo)
            st.session_state.stage = "thank_you"
            st.experimental_rerun()

if st.session_state.stage == "thank_you":
    st.header(f"Thank You, {st.session_state.name}!")
    st.write("Your survey responses have been recorded.")
    if st.button("Start a New Survey"):
        st.session_state.stage = "setup"
        st.session_state.name = ""
        st.session_state.num_comparisons = 0
        st.session_state.clubs_inv = []
        st.session_state.org_pairs = []
        st.session_state.comparisons = []
        st.experimental_rerun()
