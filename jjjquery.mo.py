import marimo

__generated_with = "0.9.31"
app = marimo.App(width="medium", app_title="jjjquery")


@app.cell(hide_code=True)
def __():
    from datetime import datetime, timedelta

    import marimo as mo


    from_ = mo.ui.datetime(value=datetime(year=2024, month=1, day=1))

    mo.md(
        f"""
        # jjjquery 🥁 Triple J-Query

        {mo.image('https://raw.githubusercontent.com/eidorb/jjjquery/refs/heads/main/image.jpeg', rounded=True).center()}

        It looks like it's simple to get started with [ABC Radio Wrapper](https://github.com/MatthewBurke1995/ABC-Radio-Wrapper).

        Let's search for the first song played from the beginning of the new year (in UTC) {from_}.
        """
    )
    return datetime, from_, mo, timedelta


@app.cell
def __(ABCRadio, from_, mo, timedelta):
    from dataclasses import asdict

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
                mo.image(first_radio_song.song.album.artwork.url),
                mo.md(
                    rf"""
                    **{first_radio_song.song.title}**  
                    by _{', '.join(artist.name for artist in first_radio_song.song.artists)}_  
                    from _{first_radio_song.song.album.title}_  
                    played at {first_radio_song.played_time:%c}  
                    on `{first_radio_song.channel}`
                    """
                ),
            ],
            justify="start",
            align="start",
        )
    )
    return


@app.cell
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
                        mo.image(src=recently_played[0].song.album.artwork.sizes[0].url),
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


@app.cell(hide_code=True)
def __(datetime, mo):
    """
    Main and only module used to search through the abcradio API.

    ABCRadio class is used to conduct the search. The other classes
    are used to provide structured data and functionality to the result

    """
    # from __future__ import annotations not required

    from dataclasses import dataclass

    # from datetime import datetime already imported by us
    from typing import Any, Iterator, List, Optional, TypedDict, cast

    import requests
    from typing_extensions import Unpack

    BASE_URL = "https://music.abcradio.net.au/api/v1/plays/search.json"


    class ABCRadio:
        """
        API wrapper for accessing playlist history of various
        Australian Broadcasting Corporation radio channels

        """

        def __init__(self) -> None:
            """
            Initialize the ABCRadio class for searching
            """

            self.available_stations: List[str] = (
                "jazz,dig,doublej,unearthed,country,triplej,classic,kidslisten".split(",")
            )
            self.BASE_URL: str = BASE_URL
            self.latest_search_parameters: Optional[RequestParams] = None

        def search(self, **params: Unpack[RequestParams]) -> "SearchResult":
            """Send request to abc radio API endpoint and create SearchResult instance

            Parameters
            ----------
            **params: RequestParams
                params["channel"]:str any of channels in self.available_stations
                params['startDate']: datetime
            """

            query_url = self.BASE_URL + self.construct_query_string(**params)
            r = requests.get(query_url)
            json_respose = r.json()
            result = SearchResult.from_json(json_input=json_respose)
            self.latest_offset = result.offset
            self.latest_search_parameters = cast(RequestParams, params)
            return result

        @staticmethod
        def construct_query_string(**params: Unpack[RequestParams]) -> str:
            """
            Construct query string to communicate with ABC radio API


            Returns
            _______
            str
                e.g."?from=2020-04-30T03:00:00.000000Z&station=triplej&offset=0&limit=10"
                internally this will return the keys order:'from','to','station',''offset','limit'
                although the ordering is not a requirement of the underlying web API
            """
            from_ = params.pop("from_", None)
            to = params.pop("to", None)
            station = params.pop("station", None)
            offset = params.pop("offset", None)
            limit = params.pop("limit", None)
            params_list = []
            if from_ is not None:
                params_list.append("from=" + from_.strftime("%Y-%m-%dT%H:%M:%S.%fZ"))
            if to is not None:
                params_list.append("to=" + to.strftime("%Y-%m-%dT%H:%M:%S.%fZ"))
            if station is not None:
                params_list.append("station=" + str(station))
            if offset is not None:
                params_list.append("offset=" + str(offset))
            if limit is not None:
                params_list.append("limit=" + str(limit))

            if len(params_list) >= 1:
                return "?" + "&".join(params_list)
            else:
                return ""

        def continuous_search(
            self, **params: Unpack[RequestParams]
        ) -> Iterator[SearchResult]:
            """
            generate next set of search results each time the function is called.

            Examples
            --------
            for searchresult in ABC.continuous_search():
                    #see SearchResult documentation for usage from here.

            Warnings
            --------
            if parameters are not added to the continuous_search and the
            program flow is not controlled then allowing the generator to
            continuously generate results will lead to roughly a million
            requests to the underling API (~720,000 as of Jan 2023)

            """

            initial_search = self.search(**params)
            yield initial_search
            total = initial_search.total
            offset = initial_search.offset
            limit = initial_search.limit
            while offset + limit < total:
                offset = offset + limit
                params["offset"] = offset
                yield self.search(**params)


    class RequestParams(TypedDict, total=False):
        """
        **kwarg arguments to be used when searching in the ABC web api

        Parameters
        ----------
        from_: datetime
            The earliest data starts from "2014-04-30T03:00:04+00:00"

        to: datetime
            to value should be greater than from_

        limit: int
            number of results to display in a single request, effective limit is 100

        offset: int
            index at which to start returning results, you can iterate through all
            radio plays by updating this value. See continuous_search for an example
            implementation.
        station: str
           any one of: "jazz,dig,doublej,unearthed,country,triplej,classic,kidslisten"
        """

        from_: datetime
        to: datetime
        limit: int
        offset: int
        station: str


    @dataclass
    class RadioSong:
        """
        Dataclass for each entity returned from ABCradio.search,
        A RadioSong is a Song played at a specific time on a specific channel.


        Attributes
        ----------
        played_time: datetime
            original playtime, including timezone information

        channel: str
            Name of channel in which song was played
            e.g. "triplej","doublej","classic","jazz","unearthed","country"

        song: Song
            contains metadata of the song including artist and album details

        """

        played_time: datetime
        channel: str
        song: Song

        @classmethod
        def from_json(cls, json_input: dict[str, Any]) -> RadioSong:
            """
            Create RadioSong instance based on json_input

            Parameters
            ----------
            json_input : dict[str,Any]
                In the format of:
                    {"entity":"Play",
                     "arid":"...",
                     "played_time":"2020-01-01T12:00:00+00:00"
                     "service_id":"triplej"
                     "recording":...,   # Song details (see Song class for more details)
                     "release": ...     # Album details (see Album class for more details)
                     }

            Returns
            _______
            RadioSong
            """
            song = Song.from_json(json_input)
            return cls(
                played_time=datetime.fromisoformat(json_input["played_time"]),
                channel=json_input["service_id"],
                song=song,
            )


    @dataclass
    class SearchResult:
        """
        Dataclass returned from ABCRadio.search
        """

        total: int
        offset: int
        limit: int
        radio_songs: List["RadioSong"]

        @classmethod
        def from_json(cls, json_input: dict[str, Any]) -> SearchResult:
            """
            Create hierarchy of objects using the result of a single request.
            To see the expected json_format: https://music.abcradio.net.au/api/v1/plays/search.json
            """

            radio_songs = []
            for radio_song in json_input["items"]:
                radio_songs.append(RadioSong.from_json(radio_song))
            return cls(
                total=json_input["total"],
                offset=json_input["offset"],
                limit=json_input["limit"],
                radio_songs=radio_songs,
            )


    @dataclass
    class Song:
        """
        Dataclass to represent a song

        """

        title: str
        duration: int
        artists: List["Artist"]
        album: Optional[Album]
        url: Optional[str]

        @classmethod
        def from_json(cls, json_input: dict[str, Any]) -> Song:
            """
            Create Song instance based on json_input

            Parameters
            ----------
            json_input : dict[str,Any]
                In the format of:
                    {"entity":"Play",
                     "arid":"...",
                     "played_time":"2020-01-01T12:00:00+00:00",
                     "service_id":"triplej",
                     "recording":...,   # Song details
                     "release": ...     # Album details
                     }


            Returns
            _______
            Song
            """
            try:
                # Occassionally release information is not present or only exists
                # under recordings.releases json key
                json_release = (
                    json_input["release"]
                    if json_input["release"]
                    else json_input["recording"]["releases"][0]
                )
                album = Album.from_json(json_release)
                artists = []
                for artist in json_release["artists"]:
                    artists.append(Artist.from_json(artist))
            except (KeyError, IndexError, TypeError):
                artists = []
                album = None

            url = Song.get_url(json_input)
            return cls(
                title=json_input["recording"]["title"],
                duration=json_input["recording"]["duration"],
                artists=artists,
                album=album,
                url=url,
            )

        @staticmethod
        def get_url(json_input):
            """
            Occassionally the url to musicbrainz will be missing,
            make the proper check and return the url if it exists
            otherwise return null
            """
            if len(json_input["recording"]["links"]) >= 1:
                return json_input["recording"]["links"][0]["url"]
            else:
                return None


    @dataclass
    class Artist:
        """
        Dataclass to represent Artists


        Attributes
        ----------
        url: Optional[str]
            url that points to musicbrainz info page for the artist

        name: str
            Name of the artist e.g. "Justin Bieber"

        is_australian: Optional[bool]
            Almost always will be null, the underlying REST api rarely provides a value
        """

        url: Optional[
            str
        ]  # http://musicbrainz.org/ws/2/artist/5b11f4ce-a62d-471e-81fc-a69a8278c7da\?inc\=aliases
        name: str
        is_australian: Optional[bool]

        @classmethod
        def from_json(cls, json_input: dict[str, Any]) -> Artist:
            """
            Construct the Artist object from the json representation in
            https://music.abcradio.net.au/api/v1/plays/search.json

            """
            if json_input["is_australian"] is None:
                is_australian = None
            else:
                is_australian = bool(json_input["is_australian"])
            if len(json_input["links"]) >= 1:
                url = json_input["links"][0]["url"]
            else:
                url = None
            return cls(url=url, name=json_input["name"], is_australian=is_australian)


    @dataclass
    class Album:
        """
        Dataclass to represent an album (referred to as "releases" in underlying web API).
        A song can be featured on several albums.


        """

        url: Optional[str]
        title: str
        artwork: Optional[Artwork]
        release_year: Optional[int]

        @classmethod
        def from_json(cls, json_input: dict[str, Any]) -> Album:
            try:
                artwork = Artwork.from_json(json_input["artwork"][0])
            except IndexError:
                artwork = None

            return cls(
                url=Album.get_url(json_input),
                title=json_input["title"],
                release_year=int(json_input["release_year"])
                if json_input["release_year"]
                else None,
                artwork=artwork,
            )

        @staticmethod
        def get_url(json_input):
            if len(json_input["links"]) >= 1:
                return json_input["links"][0]["url"]
            else:
                return None


    @dataclass
    class Artwork:
        """
        Dataclass to represent the artwork of an associated Album.
        Each album can have several artworks and each artwork can have several
        image formats/sizes.

        """

        url: str
        type: str
        sizes: List[ArtworkSize]

        @classmethod
        def from_json(cls, json_input: dict[str, Any]) -> Artwork:
            sizes: List[ArtworkSize] = []
            for size in json_input["sizes"]:
                sizes.append(ArtworkSize.from_json(size))
            return Artwork(url=json_input["url"], type=json_input["type"], sizes=sizes)


    @dataclass
    class ArtworkSize:
        """
        Dataclass to represent the image format/size for each artwork.
        Most typical use case is providing large images or thumbnails for
        each different interface.
        """

        url: str
        width: int
        height: int
        aspect_ratio: str

        @classmethod
        def from_json(cls, json_input: dict[str, Any]) -> ArtworkSize:
            return cls(
                url=json_input["url"],
                width=json_input["width"],
                height=json_input["height"],
                aspect_ratio=json_input["aspect_ratio"],
            )

        @property
        def aspect_ratio_float(self) -> float:
            width_ratio, height_ratio = self.aspect_ratio.split("x")
            return int(width_ratio) / int(height_ratio)


    mo.md(
        "[abc_radio_wrapper.py](https://github.com/MatthewBurke1995/ABC-Radio-Wrapper/blob/main/abc_radio_wrapper/abc_radio_wrapper.py) inlined for now."
    )
    return (
        ABCRadio,
        Album,
        Any,
        Artist,
        Artwork,
        ArtworkSize,
        BASE_URL,
        Iterator,
        List,
        Optional,
        RadioSong,
        RequestParams,
        SearchResult,
        Song,
        TypedDict,
        Unpack,
        cast,
        dataclass,
        requests,
    )


if __name__ == "__main__":
    app.run()
