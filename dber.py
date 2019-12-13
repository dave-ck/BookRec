import json
import os
from scipy.sparse.linalg import svds
import numpy as np
import pandas as pd

# dataset source:
# @article{goodbooks2017,
#     author = {Zajac, Zygmunt},
#     title = {Goodbooks-10k: a new dataset for book recommendations},
#     year = {2017},
#     publisher = {FastML},
#     journal = {FastML},
#     howpublished = {\url{http://fastml.com/goodbooks-10k}},
# }
# ratings.csv dataset truncated to 100'000 ratings from 6 million for portability and speed


ratings_data = pd.read_csv("./dataset/ratings.csv")
books_data = pd.read_csv("./dataset/truncated_books.csv")
# print(sorted(ratings_data))
# print(sorted(books_data))

r_df = pd.DataFrame(ratings_data, columns=['book_id', 'rating', 'user_id'], dtype=int)
# remove unnecessary entries from books data, maintain only ratings information and book_id:title mapping
b_df = pd.DataFrame(books_data,
                    columns=['book_id', 'title', 'average_rating', 'ratings_1', 'ratings_2', 'ratings_3',
                             'ratings_4', 'ratings_5', 'ratings_count', 'authors'])

b_df['book_id'] = b_df['book_id'].apply(pd.to_numeric)
b_df['ratings_count'] = b_df['ratings_count'].apply(pd.to_numeric)
preds_df = None

def recalculate():
    global preds_df, r_df
    R_df = r_df.pivot(index='user_id', columns='book_id', values='rating').fillna(0)
    R = R_df.values
    user_ratings_mean = np.mean(R, axis=1)
    R_demeaned = R - user_ratings_mean.reshape(-1, 1)
    k = min(*R_demeaned.shape, 51) - 1  # allow less than 50
    U, sigma, Vt = svds(R_demeaned, k=k)
    sigma = np.diag(sigma)
    all_user_predicted_ratings = np.dot(np.dot(U, sigma), Vt) + user_ratings_mean.reshape(-1, 1)
    preds_df = pd.DataFrame(all_user_predicted_ratings, columns=R_df.columns)


def user_rating_history(user_id):
    user_data = r_df[r_df.user_id == user_id]
    if user_data.empty:
        return json.dumps({'book_id': {}})  # return compact empty JSON
    user_full = (user_data.merge(b_df, how='left', left_on='book_id', right_on='book_id').
                 sort_values(['average_rating'], ascending=False))
    return user_full.to_json()


# adapted from https://beckernick.github.io/matrix-factorization-recommender/
def recommend_books(user_id, num_recommendations=5):
    global recs_up_to_date, b_df, preds_df
    if not recs_up_to_date:
        recalculate()
        recs_up_to_date = True
    # if there is no information to base recommendations off of for this user
    if user_rating_history(user_id) == json.dumps({'book_id': {}}):
        # return the top-rated num_recommendations book which have at least 50 ratings
        topN = b_df[b_df['ratings_count'] > 50].sort_values(['average_rating'], ascending=False).iloc[
               :num_recommendations, :-1]
        return topN.to_json()
    user_row_number = user_id - 1  # UserID starts at 1, not 0
    sorted_user_predictions = preds_df.iloc[user_row_number].sort_values(ascending=False)
    user_data = r_df[r_df.user_id == user_id]
    user_full = (user_data.merge(b_df, how='left', left_on='book_id', right_on='book_id').
                 sort_values(['rating'], ascending=False))
    recommendations = (b_df[~b_df['book_id'].isin(user_full['book_id'])].
                           merge(pd.DataFrame(sorted_user_predictions).reset_index(),
                                 how='left',
                                 left_on='book_id',
                                 right_on='book_id').
                           rename(columns={user_row_number: 'Predictions'}).
                           sort_values('Predictions', ascending=False).
                           iloc[:num_recommendations, :-1])
    return recommendations.to_json()


def add_rating(uid, book_id, user_rating):
    global b_df, r_df, recs_up_to_date
    if user_rating not in [1, 2, 3, 4, 5]:
        raise ValueError("Ratings must be integers between 1 and 5 inclusive. {} given.".format(user_rating))
    remove_rating(uid, book_id)  # remove rating if it exists
    ratings_row = {'book_id': book_id, 'rating': user_rating, 'user_id': uid}
    r_df = r_df.append(ratings_row, ignore_index=True)
    old_avg = unwrap(b_df.loc[b_df.book_id == book_id, 'average_rating'])
    old_count = unwrap(b_df.loc[b_df.book_id == book_id, 'ratings_count'])
    b_df.loc[b_df.book_id == book_id, 'ratings_' + str(user_rating)] += 1  # increment the count for the rating
    b_df.loc[b_df.book_id == book_id, 'ratings_count'] += 1  # increment the count for the rating
    new_avg = (user_rating + old_count * old_avg) / (old_count + 1)
    b_df.loc[b_df.book_id == book_id, 'average_rating'] = new_avg
    recs_up_to_date = False


def rating_exists(uid, book_id):
    return not r_df.loc[(r_df['user_id'] == uid) & (r_df['book_id'] == book_id), 'rating'].empty


def remove_rating(uid, book_id):
    global b_df, r_df, recs_up_to_date
    # if not rating_exists(uid, book_id):
    #     print("Rating didn't exist: ({}, {})".format(uid, book_id))
    #     return
    # find the old rating so b_df can be appropriately updated
    if not rating_exists(uid, book_id):
        print("Rating already non-existant: uid{}, book_id{}".format(uid, book_id))
        return
    print("RDF global")
    print(r_df)
    print("RDF zoomd, uid=", uid)
    print(r_df[(r_df['user_id'] == uid)])
    user_rating = unwrap(r_df.loc[(r_df['user_id'] == uid) & (r_df['book_id'] == book_id), 'rating'])
    r_df = r_df[(r_df['user_id'] != uid) | (r_df['book_id'] != book_id)]
    print("Rating to remove:", user_rating)
    old_avg = unwrap(b_df.loc[b_df.book_id == book_id, 'average_rating'])
    old_count = unwrap(b_df.loc[b_df.book_id == book_id, 'ratings_count'])
    b_df.loc[b_df.book_id == book_id, 'ratings_' + str(user_rating)] -= 1  # decrement the count for the rating
    b_df.loc[b_df.book_id == book_id, 'ratings_count'] -= 1  # decrement the count for the rating
    new_avg = (-1 * user_rating + old_count * old_avg) / (old_count - 1)
    b_df.loc[b_df.book_id == book_id, 'average_rating'] = new_avg
    recs_up_to_date = False


def unwrap(pd_wrapped_value):
    return pd_wrapped_value[pd_wrapped_value.keys()[0]]


def pattern_matches(user_id, pattern, num_matches=5):
    global b_df, r_df
    # if there is no information to base recommendations off of for this user
    user_data = r_df[r_df.user_id == user_id]
    user_full = pd.merge(b_df, user_data, how='left', on='book_id', sort=False)
    return user_full[user_full.title.str.contains(pattern)].to_json()


recalculate()
recs_up_to_date = True
