import socket
try:
    from theme import replace_posts_with_topics
except FileNotFoundError:
    print('LDA модель не обучена!\nЧтобы сделать это - используйте команду'
          ' "python3 trainmodel.py --count COUNT" ')
    exit(0)
try:
    from save_reddit_data import RedditUser
except FileNotFoundError:
    print('Модель анализа тональности не обучена!\nЧтобы сделать это - '
          'используйте команду "python3 train.py" ')
    exit(0)


def test_internet():
    try:
        socket.gethostbyaddr('www.yandex.ru')
    except socket.gaierror:
        return False
    return True


if __name__ == '__main__':
    if not test_internet():
        print("Отсутствует интернет соединение, "
              "проверьте подключение и повторите попытку!")
        exit(0)
    person_id = input("Введите идентификатор пользователя:")
    user = RedditUser(person_id)
    user.get_user_data()
    comments_and_posts = user.get_comments_and_posts()
    tone_dict = user.get_tone_dict(comments_and_posts)
    user.save_user_data(tone_dict)
    positive_posts, negative_posts = user.load_user_data()
    pos_topics_with_tone = replace_posts_with_topics(positive_posts)
    neg_topics_with_tone = replace_posts_with_topics(negative_posts)
    attitude_of_user = user.calculate_user_attitude(
        pos_topics_with_tone, neg_topics_with_tone)
    user.print_and_save_user_attitude(attitude_of_user)
