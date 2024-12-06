"""Triple J-Query!"""

from pprint import pp

from abc_radio_wrapper import ABCRadio

if __name__ == "__main__":
    abc_radio = ABCRadio()
    for radio_song in abc_radio.search().radio_songs:
        pp(radio_song)
        break  # for now
