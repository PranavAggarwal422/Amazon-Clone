def calculate_score(product):
    score = 0
    score += product.rating * 20
    score += min(product.num_reviews / 1000, 10)
    score += min(product.popularity_score / 1000, 10)
    return score
