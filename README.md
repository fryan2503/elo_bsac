# Student Organization ELO Rating System

This project, created for the **Business Student Advisory Council (BSAC) at Miami University**, aims to identify the key factors that set apart high-performing student organizations. We do this through an ELO rating system that compares organizations and adjusts their ratings based on survey results.

## Overview

This project uses a Flask-based web application to allow users to compare student organizations in terms of performance. The results are then stored in a MongoDB database, and the organizations' ratings are updated using an ELO rating algorithm.

### Key Components

- **Python Libraries**: The project uses various Python libraries such as `Flask` for web development, `pandas` and `numpy` for data manipulation, `pymongo` for interacting with MongoDB, and standard libraries like `random` and `datetime` for other functionalities.

- **MongoDB Integration**: Data is stored in a MongoDB collection hosted on a university server. MongoDB is used for storing survey responses and updating organization ratings.

# ELO Rating System

The ELO rating system is used to calculate the relative skill levels of student organizations based on pairwise comparisons. It updates ratings based on the outcome of matches between two organizations.

# ELO Rating System

The ELO rating system is used to calculate the relative skill levels of student organizations based on pairwise comparisons. It updates ratings based on the outcome of matches between two organizations.

## ELO Rating Formula

The ELO rating formula is used to adjust ratings after each match:

$$
R_{\text{new}} = R_{\text{current}} + K \times (\text{Outcome} - E)
$$

- \( R_{\text{new}} \): New rating of the organization.
- \( R_{\text{current}} \): Current rating of the organization.
- \( K \): The K-factor, which determines the maximum possible rating change (default is 32).
- \( \text{Outcome} \): The result of the match (1 if the organization wins, 0 if it loses).
- \( E \): Expected outcome, calculated as:

$$
E = \frac{1}{1 + 10^{\frac{R_{\text{opponent}} - R_{\text{current}}}{400}}}
$$

- \( R_{\text{opponent}} \): The rating of the opposing organization.

## How We Use the ELO System

1. **Initial Ratings**: All organizations start with a base rating of 1500.
2. **Pairwise Comparisons**: Users compare pairs of organizations through a survey. For each comparison, the chosen organization wins and the other loses.
3. **Rating Update**: After each comparison, the ratings of the two organizations are adjusted using the ELO formula.
4. **Data Storage**: Results are stored in a MongoDB database, capturing the participant's name, the organizations involved, and the comparison details.
5. **High Ranking Probability**: When selecting organizations for comparison, we introduce a bias to compare organizations with similar ratings to maintain accuracy.

This system helps us identify top-performing student organizations based on survey feedback and derive insights from their relative ratings.

### Example Insight

Using this system, we can produce insights such as:

> "Top quartile of student organizations that hold regular elections outperform the bottom quartile by 3x in terms of ELO rating."

This allows us to quantify the impact of specific factors on student organization performance.
 as:

> "Top quartile of student organizations that hold regular elections outperform the bottom quartile by 3x in terms of ELO rating."

This allows us to quantify the impact of specific factors on student organization performance.
