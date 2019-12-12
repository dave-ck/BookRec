import time

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
books_data = pd.read_csv("./dataset/books.csv")
print(sorted(ratings_data))
print(sorted(books_data))

# may wish to truncate to some shorter list to see effects of removing ratings for books with few ratings
truncate_to = 10000  # increasing above 100k will have no effect; csv file is truncated to 100k.
r_df = pd.DataFrame(ratings_data[:truncate_to], columns=['book_id', 'rating', 'user_id'], dtype=int)
# remove unnecessary entries from books data, maintain only ratings information and book_id:title mapping
b_df = pd.DataFrame(books_data[:10000],
                    columns=['book_id', 'title', 'average_rating', 'ratings_1', 'ratings_2', 'ratings_3',
                             'ratings_4', 'ratings_5', 'ratings_count', 'authors'])

start = time.time()
b_dict = b_df.to_dict()
print("Dict convert done")
for key in b_dict['book_id'].keys():
    book_id = b_dict['book_id'][key]
    total_ratings_count = 0
    total_of_ratings = 0
    for rating_value in range(1, 6):
        # count2 = r_df.loc[(r_df.book_id == book_id) & (r_df.rating == rating_value)].shape[0]
        count = r_df.loc[(r_df.book_id == book_id) & (r_df.rating == rating_value)].count()['book_id']
        # assert count == count2
        total_ratings_count += count
        total_of_ratings += count * rating_value
        b_dict['ratings_' + str(rating_value)][key] = count
    if total_ratings_count:
        mean_rating_value = total_of_ratings / total_ratings_count
    else:
        mean_rating_value = np.nan
    b_dict['average_rating'][key] = mean_rating_value
    b_dict['ratings_count'][key] = total_ratings_count

print("Done processing dict after: ", time.time() - start)
b_df = pd.DataFrame(b_dict)
b_df.to_csv('./dataset/truncated_books.csv')
print("Back to df after: ", time.time() - start)

print(b_df.head())
quit()
b_df['book_id'] = b_df['book_id'].apply(pd.to_numeric)


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
    user_full = (user_data.merge(b_df, how='left', left_on='book_id', right_on='book_id').
                 sort_values(['rating'], ascending=False))
    return user_full.to_json()


# adapted from https://beckernick.github.io/matrix-factorization-recommender/
def recommend_books(user_id, num_recommendations=5):
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


def add_rating(uid, book_id, rating):
    global b_df, r_df
    if book_id not in range(1, 6):
        raise ValueError("Book IDs must be integers between 1 and 5 inclusive.")
    ratings_row = {'book_id': book_id, 'rating': rating, 'user_id': uid}
    r_df = r_df.append(ratings_row, ignore_index=True)
    # todo: update the books df
    print(sorted(b_df))


def remove_rating(uid, book_id):
    global b_df, r_df
    # find the old rating so b_df can be appropriately updated
    user_rating = unwrap(r_df.loc[(r_df['user_id'] != uid) | (r_df['book_id'] != book_id), 'rating'])
    old_avg = unwrap(b_df.loc[b_df.book_id == book_id, 'average_rating'])
    old_count = unwrap(b_df.loc[b_df.book_id == book_id, 'ratings_count'])
    print("avg_old:", old_avg)
    print("old_count:", old_count)
    b_df.loc[b_df.book_id == book_id, 'ratings_' + str(user_rating)] -= 1  # decrement the count for the rating
    b_df.loc[b_df.book_id == book_id, 'ratings_count'] -= 1  # decrement the count for the rating

    r_df = r_df[(r_df['user_id'] != uid) | (r_df['book_id'] != book_id)]
    # df = df[(df['lib'] != 'yee_2') & (df['qty1'] != '420')]


def unwrap(pd_wrapped_value):
    return pd_wrapped_value[pd_wrapped_value.keys()[0]]


remove_rating(2, 2318)
recalculate()
print(recommend_books(user_id=2, num_recommendations=10))

print(user_rating_history(user_id=2))
