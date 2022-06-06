from datetime import datetime
from app.get_codes_twitter import get_date, get_code, get_reward, get_game, get_expiration
import pytest


test_tweet_data = [
    'SHiFT CODE\n\nGame: WONDERLANDS\nReward: 1 Skeleton Key\nExpires: 09 Jun 2022 05:00 UTC\n\n'
    '3BRTJ-5K659-K5355-BTB3T-633F3\n\nRedeem in-game or at https://t.co/g7ait1JIre\n\nhttps://t.co/P27YfpHImm',
    'SHiFT CODE\n\nGame: BORDERLANDS 3\nReward: Shrine Saint Head (Amara)\n\n'
    'KSWJJ-J6TTJ-FRCF9-X333J-5Z6KJ\n\nRedeem in-game or at https://t.co/g7ait1KggM\n\nhttps://t.co/RzEVvZhAnN',
    'SHiFT CODE\n\nGame: WONDERLANDS\nReward: 1 Skeleton Key\nExpires: 02 Jun 2022 05:00 UTC\n\n'
    'TBRJJ-TW659-W5B5C-T3B3J-3BTBK\n\nRedeem in-game or at https://t.co/g7ait1JIre\n\nhttps://t.co/Xk5M8xJ6nQ',
    'SHiFT CODE\n\nGame: BORDERLANDS 3\nReward: Antihero Head And Saurian Skull Trinket\n\n'
    'KSK33-S5T33-XX5FS-R3BTB-WSXRC\n\nRedeem in-game or at https://t.co/g7ait1JIre\n\nhttps://t.co/WTnYHLB6od',
    'SHiFT CODE\n\nGame: WONDERLANDS\nReward: 3 Skeleton Keys\n\nW9CJT-5XJTB-RRKRS-FTJ3T-BTRKK'
    '\n\nRedeem in-game or at https://t.co/g7ait1JIre\n\nhttps://t.co/Pih3w53rmo',
    'SHiFT CODE\n\nGame: BORDERLANDS 3\nReward: Pilot Punk Head\n\nWSCBT-R5BB3-66KX9-F3JBT-ZW3JK'
    '\n\nRedeem in-game or at https://t.co/g7ait1KggM\n\nhttps://t.co/4ufI8KRyAV',

    # 'SHIFT CODE (Classic)\nBORDERLANDS: PRE-SEQUEL\n5 GOLD KEYS\nEXPIRES 08 JUNE\n\nUniversal (Twitter)\n'
    # 'CWK33-5J5C6-69BXJ-3TB3B-C5SF6\nUniversal (Facebook)\nKKK3J-T35K6-FZB6T-JBJJ3-JSFKK\n'
    # 'Redeem: https://shift.gearboxsoftware.com/rewards\nArchive: https://shift.orcicorn.com/tags/presquel/',
    # 'SHIFT CODE (Classic)\nBORDERLANDS 2\n5 GOLD KEYS\nEXPIRES 08 JUNE\n\nUniversal (Twitter)\n'
    # 'CTKJB-KBXJ9-BJXJS-3TB3J-3ZCBK\nUniversal (Facebook)\nKTC3J-TTF39-3TF3Z-T3TJB-TCFSB\n'
    # 'Redeem: https://shift.gearboxsoftware.com/rewards\nArchive: https://shift.orcicorn.com/tags/presquel/',
    # 'SHIFT CODE\nBORDERLANDS 3\n3 GOLD KEYS\nEXPIRES Unknown\n\nALL PLATFORMS\nCJ5T3-X3JBB-SJWZC-HJ5T3-SXTK6\n'
    # 'Redeem: https://shift.gearboxsoftware.com/rewards\nArchive: https://shift.orcicorn.com/tags/presquel/',
    # 'SHIFT CODE\nBORDERLANDS 3\n3 GOLD KEYS\nEXPIRES 5 JUN 06:59 UTC\nVIA TWITCH SHOW\n\nALL PLATFORMS\n'
    # 'CB53B-WJTTJ-HJCZC-HBK3T-F3RX5\nRedeem: https://shift.gearboxsoftware.com/rewards\n'
    # 'Archive: https://shift.orcicorn.com/tags/presquel/',
    # 'SHIFT CODE\nBORDERLANDS 3\n3 GOLD KEYS\n18 MAY 15:00 UTC\n\nALL PLATFORMS\nCTKB3-3TTB3-ZTWH5-9T5JJ-3TSH9\n'
    # 'Redeem: https://shift.gearboxsoftware.com/rewards\nArchive: https://shift.orcicorn.com/tags/presquel/',
    # 'SHIFT CODE (Classic)\nBORDERLANDS 2\n5 GOLD KEYS\nEXPIRES 26 MAY 03:59 UTC\nVIA FACEBOOK\n\n'
    # 'PC: K353B-CXTBW-FXBFK-JBJJJ-BSXWJ\nXB: CT5TT-BFK95-9ZX6Z-C6JTB-K3STZ\nPS: CBK3J-6RS9S-SBWZW-ZTKJ3-CBR3H\n'
    # 'Redeem: https://shift.gearboxsoftware.com/rewards\nArchive: https://shift.orcicorn.com/tags/presquel/'
]


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
def test_get_date(test_input, expected):
    # act
    parsed_date = get_date(test_input)

    # assert
    assert parsed_date == expected


@pytest.mark.parametrize(
    "test_tweet, expected_code",
    [(test_tweet_data[0], '3BRTJ-5K659-K5355-BTB3T-633F3'),
     (test_tweet_data[1], 'KSWJJ-J6TTJ-FRCF9-X333J-5Z6KJ'),
     (test_tweet_data[2], 'TBRJJ-TW659-W5B5C-T3B3J-3BTBK'),
     (test_tweet_data[3], 'KSK33-S5T33-XX5FS-R3BTB-WSXRC'),
     (test_tweet_data[4], 'W9CJT-5XJTB-RRKRS-FTJ3T-BTRKK'),
     (test_tweet_data[5], 'WSCBT-R5BB3-66KX9-F3JBT-ZW3JK')]
)
def test_get_code(test_tweet, expected_code):

    # act
    code_type, code = get_code(test_tweet)

    # assert
    assert code_type == "shift"
    assert code == expected_code


@pytest.mark.parametrize(
    "test_tweet, expected_reward",
    [(test_tweet_data[0], '1 Skeleton Key'),
     (test_tweet_data[1], 'Shrine Saint Head (Amara)'),
     (test_tweet_data[2], '1 Skeleton Key'),
     (test_tweet_data[3], 'Antihero Head And Saurian Skull Trinket'),
     (test_tweet_data[4], '3 Skeleton Keys'),
     (test_tweet_data[5], 'Pilot Punk Head')]
)
def test_get_reward(test_tweet, expected_reward):
    # act
    reward = get_reward(test_tweet)

    # assert
    assert reward == expected_reward


@pytest.mark.parametrize(
    "test_tweet, expected_game",
    [(test_tweet_data[0], 'WONDERLANDS'),
     (test_tweet_data[1], 'Borderlands 3'),
     (test_tweet_data[2], 'WONDERLANDS'),
     (test_tweet_data[3], 'Borderlands 3'),
     (test_tweet_data[4], 'WONDERLANDS'),
     (test_tweet_data[5], 'Borderlands 2')]
)
def test_get_game(test_tweet, expected_game):
    # act
    game = get_game(test_tweet)

    # assert
    assert game == expected_game


@pytest.mark.parametrize(
    "test_tweet, expected_expiration",
    [(test_tweet_data[0], datetime(datetime.now().year, 6, 9, 5, 0)),
     (test_tweet_data[1], 'Unknown'),
     (test_tweet_data[2], datetime(datetime.now().year, 6, 2, 5, 0)),
     (test_tweet_data[3], 'Unknown'),
     (test_tweet_data[4], 'Unknown'),
     (test_tweet_data[5], 'Unknown')]
)
def test_get_expiration(test_tweet, expected_expiration):
    # act
    expiration = get_expiration(test_tweet)

    # assert
    assert expiration == expected_expiration
