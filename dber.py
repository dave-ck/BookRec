from scipy.sparse.linalg import svds
import numpy as np
import pandas as pd

# adapted from https://beckernick.github.io/matrix-factorization-recommender/
ratings_data = pd.read_csv("./dataset/ratings.csv")
books_data = pd.read_csv("./dataset/books.csv")
print(sorted(ratings_data))
print(sorted(books_data))

ratings_df = pd.DataFrame(ratings_data, columns=['book_id', 'rating', 'user_id'], dtype=int)
books_df = pd.DataFrame(books_data, columns=['book_id', 'title'])

books_df['book_id'] = books_df['book_id'].apply(pd.to_numeric)
R_df = ratings_df.pivot(index='user_id', columns='book_id', values='rating').fillna(0)
R = R_df.values
user_ratings_mean = np.mean(R, axis=1)
R_demeaned = R - user_ratings_mean.reshape(-1, 1)
print(R)
print(R_demeaned)
U, sigma, Vt = svds(R_demeaned, k=50)
sigma = np.diag(sigma)
all_user_predicted_ratings = np.dot(np.dot(U, sigma), Vt) + user_ratings_mean.reshape(-1, 1)
preds_df = pd.DataFrame(all_user_predicted_ratings, columns=R_df.columns)


def recommend_movies(predictions_df, userID, books_df, original_ratings_df, num_recommendations=5):
    # Get and sort the user's predictions
    user_row_number = userID - 1  # UserID starts at 1, not 0
    sorted_user_predictions = predictions_df.iloc[user_row_number].sort_values(ascending=False)

    # Get the user's data and merge in the movie information.
    user_data = original_ratings_df[original_ratings_df.user_id == (userID)]
    user_full = (user_data.merge(books_df, how='left', left_on='book_id', right_on='book_id').
                 sort_values(['rating'], ascending=False))

    print('User {0} has already rated {1} movies.'.format(userID, user_full.shape[0]))
    print('Recommending the highest {0} predicted ratings movies not already rated.'.format(num_recommendations))

    # Recommend the highest predicted rating movies that the user hasn't seen yet.
    recommendations = (books_df[~books_df['book_id'].isin(user_full['book_id'])].
                           merge(pd.DataFrame(sorted_user_predictions).reset_index(), how='left',
                                 left_on='book_id',
                                 right_on='book_id').
                           rename(columns={user_row_number: 'Predictions'}).
                           sort_values('Predictions', ascending=False).
                           iloc[:num_recommendations, :-1]
                           )

    return user_full, recommendations


already_rated, predictions = recommend_movies(preds_df, 837, books_df, ratings_df, 10)

print(already_rated.head(10))
print(predictions.head(10))