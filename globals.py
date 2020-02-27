from random import randint
import time


def single_lander_source():
    list_of_landers = ['https://cool-giveaways.weebly.com/',
                       'https://win-google-pixel-now.weebly.com/',
                       'https://win-nintendo-switch-now.weebly.com/',
                       'https://win-a-fortune-today.weebly.com/',
                       'https://win-150-dollars-now.weebly.com/'
                       'https://amzn.to/379FhAY',
                       'https://www.pinterest.com/pin/778700591807505450/',
                       'https://www.pinterest.com/pin/778700591807505339/',
                       'https://www.pinterest.com/pin/778700591807481121/',
                       ]

    return list_of_landers[randint(0, len(list_of_landers) - 1)]


def sleep_time():
    t = randint(7, 15)
    print(f"thread sleeping for {t} seconds...")

    time.sleep(t)

    return t
