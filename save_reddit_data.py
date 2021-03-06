import requests
import sentiment_mod as s
import argparse
from createuci import Text
import json
import os


class User:
    def __init__(self, user_id,
                 pos_file='positive_posts.txt', neg_file='negative_posts.txt'):
        self.user_id = user_id
        self.pos_file = pos_file
        self.neg_file = neg_file

    def save_list_to_file(self, filepath, post_list):
        with open(filepath, 'w') as file:
            file.write('\n'.join(post_list))
        return

    def save_user_data(self, tone_dict):
        positive_posts = []
        negative_posts = []
        for post, tone in tone_dict.items():
            if tone['pos']:
                positive_posts.append(post + '=' + str(tone['pos']))
            else:
                negative_posts.append(post + '=' + str(tone['neg']))
        self.save_list_to_file(self.pos_file, positive_posts)
        self.save_list_to_file(self.neg_file, negative_posts)
        return

    def load_user_data(self):
        pos_user_data = []
        neg_user_data = []
        with open(self.pos_file, 'r') as file:
            for line in file.readlines():
                pos_user_data.append(line.rstrip('\n').split('='))
        with open(self.neg_file, 'r') as file:
            for line in file.readlines():
                neg_user_data.append(line.rstrip('\n').split('='))
        return pos_user_data, neg_user_data

    def get_tone_dict(self, post_and_commment):
        tone_dict = {}
        for item in post_and_commment.items():
            confidence_dict = {}
            tone = s.sentiment(item[1])
            if tone[0] == 'pos':
                confidence_dict['pos'] = tone[1]
                confidence_dict['neg'] = 0
            else:
                confidence_dict['neg'] = tone[1]
                confidence_dict['pos'] = 0
            if (item[0] in tone_dict):
                tone_dict[item[0]]['pos'] += confidence_dict['pos']
                tone_dict[item[0]]['neg'] += confidence_dict['neg']
            else:
                tone_dict[item[0]] = confidence_dict
        return tone_dict


class RedditUser(User):
    def __init__(self, user_id,
                 pos_file='positive_posts.txt', neg_file='negative_posts.txt'):
        super().__init__(user_id, pos_file, neg_file)

    def get_user_data(self):
        r = requests.get(
            'http://www.reddit.com/user/%s/comments/.json' % self.user_id)
        data = r.json()
        if 'error' in data.keys():
            if data['error'] == 404:
                print("Такого пользователя не существует!")
            elif data['error'] == 429:
                print("Большое количество запросов...Повторите попытку!")
            exit(0)
        user_data = []
        for child in data['data']['children']:
            if (child['data']['parent_id'] == child['data']['link_id']):
                user_data.append(child['data'])
        self.data = user_data
        return

    def get_comments_and_posts(self):
        comments_and_posts = {}
        if self.data is not None:
            for i in range(len(self.data)):
                clean_text = Text()
                post = clean_text.text_cleaning(self.data[i]['link_title'])
                comment = clean_text.text_cleaning(self.data[i]['body'])
                comments_and_posts[post] = comment
        return comments_and_posts

    def calculate_user_attitude(self, pos_topics, neg_topics):
        user_attitude = {}
        for topic in pos_topics:
            for theme, probability in topic[0]:
                pos = float(topic[1]) * probability
                try:
                    user_attitude[theme]['pos'] += pos
                except KeyError:
                    user_attitude[theme] = {'pos': 0, 'neg': 0}
                    user_attitude[theme]['pos'] += pos
        for topic in neg_topics:
            for theme, probability in topic[0]:
                neg = float(topic[1]) * probability
                user_attitude[theme]['neg'] += neg
        return user_attitude

    def print_and_save_user_attitude(self, user_attitude):
        print('Отношение пользователя к темам:')
        data = {}
        for topic, tone in user_attitude.items():
            neg = tone['neg']
            pos = tone['pos']
            total = pos + neg
            pos_percent = (pos / total) * 100
            print('Тема - ' + topic + '. Положительно на ' + str(pos_percent) + '%')
            data[topic] = {'pos': pos_percent}
        if not os.path.exists('users_results'):
            os.mkdir('users_results')
        with open('./users_results/' + self.user_id + '.json', 'w') as file:
            json.dump(data, file)
        return


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("user_id", help="идентификатор пользователя")
    parser.add_argument("--pos",
                        help="название файла для сохранения позитивных постов")
    parser.add_argument("--neg",
                        help="название файла для сохранения негативных постов")
    args = parser.parse_args()
    if args.pos and args.neg:
        user = RedditUser(args.user_id, args.pos, args.neg)
    elif args.pos:
        user = RedditUser(args.user_id, args.pos)
    elif args.neg:
        user = RedditUser(args.user_id)
        user.neg_file = args.neg
    else:
        user = RedditUser(args.user_id)
    user.get_user_data()
    comments_and_posts = user.get_comments_and_posts()
    tone_dict = user.get_tone_dict(comments_and_posts)
    user.save_user_data(tone_dict)
