from datetime import datetime

import pytest


@pytest.mark.parametrize(
    "test_input, expected",
    [('11 Jan 14:00 Sunday', datetime(datetime.now().year, 1, 11, 14, 0)),
     ('11 Jan 13:30', datetime(datetime.now().year, 1, 11, 13, 30)),
     ('11 Jan', datetime(datetime.now().year, 1, 11, 0, 0)),
     ('08 JUNE', datetime(datetime.now().year, 6, 8, 0, 0)),
     ('2 JUN 07:59 UTC', datetime(datetime.now().year, 6, 2, 7, 59)),
     ('20 APR 23:59 -0500', datetime(datetime.now().year, 4, 21, 4, 59)),
     ('20 APR 23:59 PST', datetime(datetime.now().year, 4, 21, 7, 59)),
     ('20 APR 23:59 PDT', datetime(datetime.now().year, 4, 21, 6, 59)),
     ('01 SMARCH 23:59', 'Unknown')]
)
def test_get_date(twitter_listener, test_input, expected):
    dt = twitter_listener.get_date(test_input)
    assert dt == expected


test_tweet_data = [
    'SHIFT CODE (Classic)\nBORDERLANDS: PRE-SEQUEL\n5 GOLD KEYS\nEXPIRES 08 JUNE\n\nUniversal (Twitter)\nCWK33-5J5C6-69BXJ-3TB3B-C5SF6\nUniversal (Facebook)\nKKK3J-T35K6-FZB6T-JBJJ3-JSFKK\nRedeem: https://shift.gearboxsoftware.com/rewards\nArchive: https://shift.orcicorn.com/tags/presquel/',
    'SHIFT CODE (Classic)\nBORDERLANDS 2\n5 GOLD KEYS\nEXPIRES 08 JUNE\n\nUniversal (Twitter)\nCTKJB-KBXJ9-BJXJS-3TB3J-3ZCBK\nUniversal (Facebook)\nKTC3J-TTF39-3TF3Z-T3TJB-TCFSB\nRedeem: https://shift.gearboxsoftware.com/rewards\nArchive: https://shift.orcicorn.com/tags/presquel/',
    'SHIFT CODE\nBORDERLANDS 3\n3 GOLD KEYS\nEXPIRES Unknown\n\nALL PLATFORMS\nCJ5T3-X3JBB-SJWZC-HJ5T3-SXTK6\nRedeem: https://shift.gearboxsoftware.com/rewards\nArchive: https://shift.orcicorn.com/tags/presquel/',
    'SHIFT CODE\nBORDERLANDS 3\n3 GOLD KEYS\nEXPIRES 5 JUN 06:59 UTC\nVIA TWITCH SHOW\n\nALL PLATFORMS\nCB53B-WJTTJ-HJCZC-HBK3T-F3RX5\nRedeem: https://shift.gearboxsoftware.com/rewards\nArchive: https://shift.orcicorn.com/tags/presquel/',
    'SHIFT CODE\nBORDERLANDS 3\n3 GOLD KEYS\n18 MAY 15:00 UTC\n\nALL PLATFORMS\nCTKB3-3TTB3-ZTWH5-9T5JJ-3TSH9\nRedeem: https://shift.gearboxsoftware.com/rewards\nArchive: https://shift.orcicorn.com/tags/presquel/',
    'SHIFT CODE (Classic)\nBORDERLANDS 2\n5 GOLD KEYS\nEXPIRES 26 MAY 03:59 UTC\nVIA FACEBOOK\n\nPC: K353B-CXTBW-FXBFK-JBJJJ-BSXWJ\nXB: CT5TT-BFK95-9ZX6Z-C6JTB-K3STZ\nPS: CBK3J-6RS9S-SBWZW-ZTKJ3-CBR3H\nRedeem: https://shift.gearboxsoftware.com/rewards\nArchive: https://shift.orcicorn.com/tags/presquel/'
]


# @pytest.mark.parametrize(
#     "test_tweet, expected_code",
#     [(test_tweet_data[0], 'CWK33-5J5C6-69BXJ-3TB3B-C5SF6'),
#      (test_tweet_data[1], 'CTKJB-KBXJ9-BJXJS-3TB3J-3ZCBK'),
#      (test_tweet_data[2], 'CJ5T3-X3JBB-SJWZC-HJ5T3-SXTK6'),
#      (test_tweet_data[3], 'CB53B-WJTTJ-HJCZC-HBK3T-F3RX5'),
#      (test_tweet_data[4], 'CTKB3-3TTB3-ZTWH5-9T5JJ-3TSH9'),
#      (test_tweet_data[5], 'K353B-CXTBW-FXBFK-JBJJJ-BSXWJ')]
# )
# def test_get_code(twitter_listener, test_tweet, expected_code):
#     code_type, code = twitter_listener.get_code(test_tweet)
#
#     assert code_type == "SHiFT"
#     assert code == expected_code


@pytest.mark.parametrize(
    "test_tweet, expected_reward, expected_code, expected_game",
    [(test_tweet_data[0], '5 GOLD KEYS', 'CWK33-5J5C6-69BXJ-3TB3B-C5SF6', 'Borderlands: Pre-Sequel'),
     (test_tweet_data[1], '5 GOLD KEYS', 'CTKJB-KBXJ9-BJXJS-3TB3J-3ZCBK', 'Borderlands 2'),
     (test_tweet_data[2], '3 GOLD KEYS', 'CJ5T3-X3JBB-SJWZC-HJ5T3-SXTK6', 'Borderlands 3'),
     (test_tweet_data[3], '3 GOLD KEYS', 'CB53B-WJTTJ-HJCZC-HBK3T-F3RX5', 'Borderlands 3'),
     (test_tweet_data[4], '3 GOLD KEYS', 'CTKB3-3TTB3-ZTWH5-9T5JJ-3TSH9', 'Borderlands 3'),
     (test_tweet_data[5], '5 GOLD KEYS', 'K353B-CXTBW-FXBFK-JBJJJ-BSXWJ', 'Borderlands 2')]
)
def test_get_exp(twitter_listener, test_tweet, expected_reward, expected_code, expected_game):
    game, code_type, code, reward, expires = twitter_listener.parse_text(test_tweet, datetime.now())
    assert game == expected_game
    assert code == expected_code
    assert code_type == "SHiFT"
    assert reward == expected_reward
