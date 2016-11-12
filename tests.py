import unittest
from sentiment_mod import sentiment
from save_reddit_data import RedditUser
from createuci import WikiText, Text
from theme import get_post_topics


class TestSentimentAnalysis(unittest.TestCase):

    def test_positive(self):
        self.assertEqual(sentiment('that is great idea')[0], 'pos')

    def test_negative(self):
        self.assertEqual(sentiment('he is stupid boy')[0], 'neg')


class TestRedditUser(unittest.TestCase):

    def test_get_comment_and_post(self):
        user = RedditUser('testuser')
        user.data = [{'link_title': 'gifs',
                      'body': "Usersub is an imgur thing. Don't mindlessly "
                      "copy shit that doesn't even make sense here."}]
        expected_com_and_sub = {'gifs': 'usersub is an imgur thing don t '
                                'mindlessly copy shit that doesn t even '
                                'make sense here'}
        self.assertEqual(user.get_comments_and_posts(),
                         expected_com_and_sub)

    def test_get_post_topics(self):
        self.assertEqual(
            max(get_post_topics(
                'the nurse brought the pills'),
                key=lambda x: x[1])[0],
            'Medicine')


class TestText(unittest.TestCase):

    def test_word_correct(self):
        text = Text()
        self.assertFalse(text.is_word_correct('121'))
        self.assertFalse(text.is_word_correct('is'))
        self.assertFalse(text.is_word_correct('a'))
        self.assertTrue(text.is_word_correct('word'))

    def test_capitalize_first_letter(self):
        text = Text()
        self.assertIsNone(text.capitalize_first_letter(None))
        self.assertEqual(text.capitalize_first_letter('word'), 'Word')

    def test_get_main_article(self):
        wiki = WikiText('Programming languages')
        self.assertEqual(wiki.get_main_article(
            wiki.list_of_categories), 'Programming language')


if __name__ == '__main__':
    unittest.main()
