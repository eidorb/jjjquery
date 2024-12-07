import marimo

__generated_with = "0.9.31"
app = marimo.App(width="medium", app_title="jjjquery")


@app.cell(hide_code=True)
async def __():
    from datetime import datetime, timedelta

    import micropip

    import marimo as mo

    # Install hacked abc-radio-wrapper.
    await micropip.install(
        "https://raw.githubusercontent.com/eidorb/jjjquery/refs/heads/main/abc_radio_wrapper-0.3.0-py2.py3-none-any.hacked.whl"
    )

    from_ = mo.ui.datetime(value=datetime(year=2024, month=1, day=1))

    mo.md(
        f"""
        # jjjquery 🥁 Triple J-Query

        {mo.image('https://raw.githubusercontent.com/eidorb/jjjquery/refs/heads/main/image.jpeg', rounded=True).center()}

        It looks like it's simple to get started with [ABC Radio Wrapper](https://github.com/MatthewBurke1995/ABC-Radio-Wrapper).

        Let's search for the first song played from the beginning of the new year (in UTC) {from_}.
        """
    )
    return datetime, from_, micropip, mo, timedelta


@app.cell
def __(ABCRadio, from_, mo, timedelta):
    from dataclasses import asdict

    from abc_radio_wrapper import ABCRadio

    abc_radio = ABCRadio()
    to = from_.value + timedelta(minutes=1)
    for search_result in abc_radio.continuous_search(from_=from_.value, to=to):
        for first_radio_song in search_result.radio_songs:
            continue

    mo.md(
        f"""
        Search parameters:
        {mo.as_html(dict(from_=from_.value, to=to))}

        First played song:
        {mo.as_html(asdict(first_radio_song))}
        """
    )
    return abc_radio, asdict, first_radio_song, search_result, to


@app.cell(hide_code=True)
def __(mo):
    mo.md(r"""Can we style the song?""")
    return


@app.cell
def __(first_radio_song, mo):
    mo.output.append(
        mo.hstack(
            [
                mo.image(first_radio_song.song.album.artwork.url, rounded=True),
                mo.md(
                    f"""
                    **{first_radio_song.song.title}**  
                    by _{', '.join(artist.name for artist in first_radio_song.song.artists)}_  
                    from _{first_radio_song.song.album.title}_  
                    played at {first_radio_song.played_time:%c}  
                    on `{first_radio_song.channel}`
                    """
                ),
            ],
            justify="start",
            align="center",
        )
    )
    return


@app.cell(hide_code=True)
def __(mo):
    minutes_slider = mo.ui.slider(
        start=5, stop=90, step=5, value=30, debounce=True, show_value=True
    )
    mo.md(
        f"""
        Can we mimic the Triple J [live player](https://www.abc.net.au/triplej/live/triplej)
        and show what was played in the last {minutes_slider} minutes?
        """
    )
    return (minutes_slider,)


@app.cell(hide_code=True)
def __(abc_radio, datetime, minutes_slider, mo, timedelta):
    from datetime import timezone

    now = datetime.now(timezone.utc)
    recently_played = [
        radio_song
        for search_result in abc_radio.continuous_search(
            from_=now - timedelta(minutes=minutes_slider.value),
            to=now,
            station="triplej",
            limit=100,
        )
        for radio_song in search_result.radio_songs
    ]

    # Style the latest song differently.
    mo.output.append(
        mo.vstack(
            [
                mo.audio(
                    "https://mediaserviceslive.akamaized.net/hls/live/2038308/triplejnsw/index.m3u8"
                ),
                mo.md(
                    '<span style="color:white">'
                    + f"{recently_played[0].played_time.astimezone(timezone(timedelta(hours=10))):%I:%M %p}".lstrip(
                        "0"
                    )
                    + "</span>"
                ),
                mo.hstack(
                    [
                        mo.image(
                            src=recently_played[0].song.album.artwork.sizes[0].url
                            if recently_played[0].song.album
                            and recently_played[0].song.album.artwork
                            and recently_played[0].song.album.artwork.sizes
                            else ""
                        ),
                        mo.md(
                            f"""
                            **<span style="color:white">{recently_played[0].song.title}</span>**

                            <span style="color:white">{recently_played[0].song.artists[0].name}</span>  
                            <span style="color:white">{recently_played[0].song.album.title}</span>
                            """
                        ),
                    ],
                    justify="start",
                    align="end",
                ),
            ]
        )
        .callout()
        .style({"background-color": "#333"})
        .center()
    )

    # Display the remaining songs.
    for radio_song in recently_played[1:]:
        mo.output.append(
            mo.vstack(
                [
                    mo.vstack(
                        [
                            mo.md(
                                f"{radio_song.played_time.astimezone(timezone(timedelta(hours=10))):%I:%M %p}".lstrip(
                                    "0"
                                ),
                            ),
                            mo.hstack(
                                [
                                    mo.image(
                                        src=radio_song.song.album.artwork.sizes[0].url
                                        if radio_song.song.album
                                        and radio_song.song.album.artwork
                                        and radio_song.song.album.artwork.sizes
                                        else ""
                                    ),
                                    mo.md(
                                        f"""
                                **{radio_song.song.title}**

                                {", ".join(artist.name for artist in radio_song.song.artists)}  
                                {radio_song.song.album.title if radio_song.song.album else ""}  
                                [YouTube](https://www.youtube.com/results?search_query={" ".join(artist.name for artist in radio_song.song.artists)} {radio_song.song.title})
                                """
                                    ),
                                ],
                                justify="start",
                                align="start",
                            ),
                        ],
                        align="start",
                    ).callout()
                ]
            ).center()
        )
    return now, radio_song, recently_played, timezone


if __name__ == "__main__":
    app.run()
